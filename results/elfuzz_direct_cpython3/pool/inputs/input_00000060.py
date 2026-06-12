"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


def deinterleave_struct(flat_data: bytes, n_points: int) -> tuple[list[tuple[float, float, float]], ...]:
    """Unpack a flat binary buffer containing interleaved floats into a list of (x,y,z) tuples."""
    fmt = f">{3*n_points}f"
    point_fmt = f"(3)f"
    shape = ((n_points,), (3,))
    data = struct.unpack_from(fmt, flat_data)
    return tuple(struct.iter_unpack(point_fmt, data)[0])


# ── array — dynamic arrays, buffers and views, signed/unsigned integers ───────

class SignedArray(array.array):
    def as_unsigned(self) -> UnsignedArray:
        arr = self.copy()
        arr.byteswap()
        arr.tounsigned()
        return arr

    def to_signed(self) -> SignedArray:
        arr = self.copy()
        arr.byteswap()
        arr.tosigned()
        return arr


class UnsignedArray(array.array):
    def as_signed(self) -> SignedArray:
        arr = self.copy()
        arr.byteswap()
        arr.to_signed()
        return arr

    def to_unsigned(self) -> UnsignedArray:
        arr = self.copy()
        arr.byteswap()
        arr.touint()
        return arr


# ── Memory view — low-level access to native/C structures ─────────────────────

def create_memview(arr: UnsignedArray) -> mmap.mmap:
    """Create a memory view of an unsigned array that can be modified by C extension functions."""
    ptr = id(arr.buffer_info()[0])
    size = arr.nbytes
    flags = mmap.ACCESS_WRITE | mmap.MAP_SHARED
    fd = os.dup(sys.stdout.fileno())
    mfd = os.fdopen(fd, "r+b")
    mm = mmap.mmap(mfd.fileno(), length=size, offset=ptr, access=flags)
    return mm


def memview_write(mm: mmap.mmap, start: int, end: int, val: int):
    mm[start:end] = struct.pack(">L", val)


def memview_read(mm: mmap.mmap, start: int, end: int) -> int:
    return struct.unpack(">L", mm[start:end])[0]


# ── Pickle & copyreg ─────────────────────────────────────────────────────────

def pickled_text(obj: object) -> str:
    """Serialize an object using pickle and print it out