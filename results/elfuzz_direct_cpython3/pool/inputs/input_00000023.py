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
    }


# ── Pickle/unpickle ───────────────────────────────────────────────────────────

class DumbDict(dict):

    def __setitem__(self, key: Any, value: Any) -> None:
        raise TypeError(f"cannot modify immutable {key!r} with {type(value).__name__}")


# TODO: can we implement __reduce__ to use this?
def pickleable_dict() -> dict[Any, Any]:
    d = DumbDict({"a": 1, "b": 2})
    pickled = pickle.dumps(d)

    unpickled = pickle.loads(pickled)
    assert type(unpickled) == DumbDict, type(unpickled)
    assert all(type(k) == str for k in unpickled.keys()), type(unpickled["a"])

    del d
    return unpickled


# ── cpython internal sys internals ───────────────────────────────────────────-

def sys_module_attributes() -> dict:
    """Inspect attributes of the built-in module 'sys'."""
    attrs = [
        "__build_class__",
        "__displayhook__",
        "__excepthook__",
        "__interactivehook__",
        "__maxsize__",
        "__stderr__",
        "__stdin__",
        "__stdout__",
        "__warningregistry__",
    ]
    return {attr: getattr(sys, attr) for attr in attrs}


def sys_modules() -> dict:
    """List loaded modules by name."""
    return {m.name: m for m in sys.modules.values()}

# ── frame inspection ──────────────────────────────────────────────────────────

def get_local_names_and_values(frame: types.FrameType) -> tuple[list[str], list[object]]:
    """
    Return two lists, containing the locals' variable names and values in order.

    Also works on nested frames!
    """

    locals_list = []

    def gather_locals(locals_: dict, level: int) -> None:
        if level >= 5:
            print(f">>> Skipping too deep frame at line {frame.f_lineno}")
            return
        for var_name in sorted(locals_):
            locals_list.append((var_name, locals_[var_name]))
            try:
                next_frame = frame.f_back
                while next_frame.f_back is not None:
                    next_frame = next_frame.f_back
                    break
                if next_frame.f_lineno < frame.f_lineno -     ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


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
    b = array.array("d", [x ** 2 for x in a])

