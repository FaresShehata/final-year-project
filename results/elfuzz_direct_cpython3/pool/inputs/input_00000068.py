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
    flat = [coord for p in points for coord in p]              # flatten
    return struct.pack(fmt, *flat)


def uninterleave_struct(data: bytes) -> list[tuple[float, float, float]]:
    """Unpack a flat binary buffer into a list of (x,y,z) float tuples."""
    fmt = f">{len(data)//3}f"
    coords = struct.iter_unpack(fmt, data)
    return [(x, y, z) for (x, y, z) in coords]


test_data = [
    ((-5.0, -7.5, 9.2), (-3.5, 4.2, 1.7)),
    ((3.0,  1.0, 5.0), (1.0, -3.0, 2.0)),
]
expected = [((-4.0, -6.0, 10.2), (-4.5, 4.1, 2.4)), ((2.0,  -2.0, 6.0), (0.0, -4.0, 3.0))]
for x, y in test_data:
    assert uninterleave_struct(interleave_struct((x, y))) == expected


# ── array — binary packing ────────────────────────────────────────────────────

test_array = array.array("i", [-5, -3, 3, 5])
assert type(test_array[0]) is int       # integer array
assert type(test_array[-1]) is int      # last element is an int


class IntArray(array.ArrayType):         # custom array subclass to support __int__()
    def __index__(self) -> int:
        return self.tolower().item()


test_array = IntArray([-5, -3, 3, 5], dtype="int")
assert isinstance(test_array, IntArray)             # instance of IntArray subclass
assert type(test_array.item()) is int               # instance is an int
assert type(test_array[0]) is IntArray             # item is an IntArray
assert type(test_array[0][0]) is int                # item is an int
assert test_array.int() == -5                      # convert array to an int
assert test_array.tostring() == b'\xf5\xfc'         # convert array to a string
assert test_array.tolist() == [-5, -3, 3, 5]        # convert array to a list
assert