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

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del self.frame.f_locals["inspector"]
        del self.stack[:]
        del self.locals[:]

    def visit(self, opcode: dis.Instruction) -> bool:
        self.stack.append(opcode)
        try:
            getattr(self, f"visit_{opcode.opname}")()
        except AttributeError:
            pass
        finally:
            self.stack.pop()

    def visit_LOAD_GLOBAL(self) -> None:
        name = self.stack[-1].argval
        self.locals[name] = id(self.locals[name])

    def visit_STORE_FAST(self) -> None:
        name = self.stack[-1].argval
        self.locals[name] = id(self.locals[name])


def run_and_inspect(fn: types.FunctionType) -> types.FrameType:
    frame = inspect.currentframe().f_back
    inspector = FrameInspector(frame)

    # See https://docs.python.org/3/library/dis.html#dis.showcode
    dis.setnextinstruction(inspector.visit)
    dis.Bytecode(fn).dis()       # this is equivalent to running the following

    return frame


# ── Struct and array ──────────────────────────────────────────────────────────

def struct_struct_unpack_packing_test(test_case: Any) -> None:
    import binascii
    test_data = {
        "struct.pack": (
            ("<d", -1e-7),           # little-endian double precision, two bytes
            ("<d", 9876543210987654.0),
            (">d", 5432109876543210.0),   # big-endian double precision, two bytes
            ("<Q", 5432109876543210),     # little-endian quadword, eight bytes
            ("<Q", 1234567890123456789),
            (">Q", 9876543210987654321), # big-endian quadword, eight bytes
            ("<i", 12345),              # little-endian signed integer, four bytes
            ("<I", 123456789),          # little-endian unsigned integer, four bytes