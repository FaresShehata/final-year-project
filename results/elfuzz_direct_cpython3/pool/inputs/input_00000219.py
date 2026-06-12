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


def replace_bytecode(fn: types.FunctionType, new_fn: types.FunctionType) -> types.CodeType:
    """Replace the code object of fn with that of another function."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(code=compile(new_fn, "<repl>", "exec"))
    return new_co


def get_code(module: importlib.ModuleType) -> types.CodeType:
    """Get the code object of an imported module from its source filename."""
    loader = module.__loader__
    assert isinstance(loader, importlib._bootstrap_external.SourceFileLoader)
    # BytesIO write/read are guaranteed to be atomic on most platforms.
    buf = io.BytesIO()
    with open(loader.path, mode="rb+") as f:
        f.write(buf.getvalue())
    return compile(buf.getvalue(), loader.path, "exec")


def get_source(module: importlib.ModuleType) -> bytes:
    """Read the source code of an imported module from its source filename."""
    loader = module.__loader__
    assert isinstance(loader, importlib._bootstrap_external.SourceFileLoader)
    buf = io.BytesIO()
    with open(loader.path, mode="rb+") as f:
        buf.write(f.read())
    return buf.getvalue()


# ── ctypes for bytecode inspection ────────────────────────────────────────────

class FrameInspector(object):
    def __init__(self, frame: types.FrameType) -> None:
        self.frame = frame
        self.stack = []
        self.locals = {}

    def __enter__(self) -> FrameInspector:
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None) -> None:
        del exc_type, exc_val, exc_tb
        del self.stack, self.locals, self.frame

    @property
    def locals(self) -> dict:
        for opnum, oparg in self.frame.f_lasti:
            if opnum != dis.opmap["LOAD_GLOBAL"]:
                continue
            # The last global we want to look up is the one loaded by this call --
            # it's what will be stored in `oparg`.
            if oparg not in self.frame.f_locals:
                raise ValueError(f"no local named `{oparg}`")
            yield oparg, self.frame.f_locals[oparg]

    def get_stack(self) -> list[types.FrameType]:
        """Walk the stack until we reach the current frame    while frame is not None:
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
    b = array.array("d", [x ** 2 for x in a])

