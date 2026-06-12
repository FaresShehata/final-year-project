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
        co_consts=tuple(),             # default empty tuple as co_consts
        co_filename=f"/dev/null",      # dummy filename; needed on Windows
        co_name=new_name,              # use our own string here
        **co.__dict__,                  # copy all other attributes from original
    )
    return types.FunctionType(new_co, fn.__globals__)


def print_code(fn) -> None:
    """Print out the contents of this function's code object."""
    co = fn.__code__
    print(f"code size: {co.co_size}")
    print(f"name: {fn.__name__}\n  docstring:\n{co.co_consts[0]}")
    print(dis.codeinfo_to_string(co))


def get_source(fn) -> str | None:
    """Read the source code for a given function using the appropriate loader.

    Returns a string containing the source or None if no source could be found.
    """
    if isinstance(fn, types.CodeType):                # function is already compiled
        return None                                   # ...we can't read that

    module_name = fn.__module__.split(".")[-1]
    try:
        loader = importlib.machinery.SourceFileLoader(module_name, fn.__code__.co_filename)
    except FileNotFoundError:      # module not available as a source file
        return None
    exec(compile(loader.get_data(), loader.path, "exec"), globals())    # run it!
    return loader.source_code


# ── ctypes ────────────────────────────────────────────────────────────────────

def dump_bytes(bytes_obj: bytes) -> None:
    """Dump the contents of a bytes-like object to standard output."""
    for byte in bytes_obj:
        print(byte, end=" ")
        if byte < 32 or byte > 127:
            print(" ", end="")
        print(chr(byte) if 32 <= byte < 127 else ".", end="")
    print("\n")


def cast_pointer(ptr: int, length: int) -> ctypes.Array:
    """Cast an integer pointer to a ctypes array of specified length."""
    return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_char * length)).contents


def array_as_buffer(array: array.array) -> bytes:
    """Convert an array to a plain bytes instance."""
    ptr = id(array.buffer_info()[0])
    length = array.itemsize * array.nbytes
    return cast_pointer(ptr, length).raw


# ── Struct — binary
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
