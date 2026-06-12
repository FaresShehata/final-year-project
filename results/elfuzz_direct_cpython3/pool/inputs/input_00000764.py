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
    header = struct.pack(HEADER_FMT, magic, version_major, version_minor, tag)
    return header + b"\x00" * (HEADER_SIZE - len(header))  # padding to align with 8-byte boundary


def unpack_header(buf: memoryview) -> tuple[int, int, bytes]:
    return struct.unpack(HEADER_FMT, buf[:HEADER_SIZE])


# ── Array packing ─────────────────────────────────────────────────────────────

STRING_1MB = "".join(chr(i) for i in range(256)) * 1024 ** 2
SINGLE_QUOTED_STRING = "'" + STRING_1MB + "'"
DOUBLE_QUOTED_STRING = '"' + STRING_1MB + '"'

BIGINTS = [
    0xDEADBEEF,
    0xDEADBEEFDEADBEEF,
    0xDEADBEEFFEEDBEBEF,
    0xDEADBEFAAAAAAAAAA,
]


def pack_array(array_type: str, data: bytes | bytearray) -> memoryview:
    return array.array(array_type, data).tobytes()


def unpad(data: bytes | bytearray) -> bytearray:
    return bytearray(data[:-data[-1]])


# ── CopyReg, Marshal, Pickle, WeakRef, SysInternals ───────────────────────────

# Copied from https://github.com/python/cpython/blob/3.7/Lib/pickletools.py#L191-L204
COPYREG_FUNCS = {
    "<module>": {},
}


def copy_reg(funcs: dict[str, types.Type[types.FunctionType]]) -> None:
    COPYREG_FUNCS["<module>"].update(funcs)


# ── Imports, Modules, Fallbacks, Metadata ──────────────────────────────────────


class MyModule(importlib.machinery.ExtensionFileLoader):

    loader = importlib.abc.Loader.from_spec(spec=None)

    def load_module(self, fullname: str) -> types.ModuleType:
        pass


def get_metadata(module: types.ModuleType) -> dict[str, Any]:
    return module.__dict__.copy()


def set_metadata(module: types.ModuleType, metadata: dict[str, Any]) -> None:
    module.__dict__.clear()
    module.__dict__.update(metadata)


# ── MemoryView, GC, Tracemalloc, Weakref, Slots ────────────────────────────────

def create_memoryview(bytes_: bytes) -> memoryview:
    return memoryview(bytes_)