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


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    assert isinstance(a, ctypes.Array)         # type hint
    assert a.typecode == "d"                   # what's stored
    # convert to/from memoryview
    m = memoryview(a)
    assert isinstance(m, memoryview)
    print(f"type({m}): {type(m)}")
    assert m.format == "d"                     # what's viewed as contiguous data
    assert m.itemsize == 8                     # item size in bytes
    assert m.readonly == False                 # can be mutated?
    assert m.tobytes() == a.tostring()         # view as string
    return locals()


def view_and_modify(array_like: list[int]) -> tuple[list[int], memoryview]:      # noqa: D205,D400
    """Create a `memoryview` from an array-like container and modify it."""
    mv = memoryview(array_like)       # create a view on the underlying buffer
    del mv[4:]                        # remove 4 elements starting at idx 4
    mv[:] = [i + 2 for i in mv]       # modify all remaining values by adding 2
    return array_like, mv             # return modified containers


# ── pickle & marshal ─────────────────────────────────────────────────────────-

def pickling(obj: Any) -> Any:
    """Serialize an arbitrary object using both pickle and marshal."""
    serialized = marshal.dumps(obj)
    deserialized = marshal.loads(serialized)
    try:
        unserialized = pickle.loads(serialized)
    except Exception as e:
        raise AssertionError(f"Pickle load failed:\n{e}\n\nSerialized:\n{serialized}\n")
    assert obj == deserialized
    assert obj == unserialized
    return unserialized


def serializing(obj: Any) -> Any:
    """Serialize an arbitrary object using both pickle and marshal."""
    serialized = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    deserialized = pickle.loads(serialized)
    unserialized = marshal.loads(serialized)
    assert obj == deserialized
    assert obj == unserialized
    return unserialized