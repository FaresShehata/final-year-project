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
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)


def make_magic_function() -> types.FunctionType:
    def f(x): return x**x
    f.__module__ = "__main__"
    return f


# ── low-level bytecodes ───────────────────────────────────────────────────────


int_type_codes = {i: hex(i) for i in range(-16, 17)}
float_type_codes = {
    i: (f"{i / 100:.2g}" if abs(i) < 10 ** 5 or abs(i) > 10 ** -5 else f"{i}")
    for i in range(20)
}

binary_ops = ((b"add", "ADD"), (b"fadd", "FADD"), (b"isub", "ISUB"))
unary_ops = (
    (b"neg", "NEG"),
    (b"not_", "NOT_"),
    (b"inv", "INV"),
    (b"abs_", "ABS_"),
)

for op, opcode in binary_ops + unary_ops:
    print(f"\n{opcode}:\n")
    dis.show_bytecode(op)


class CustomOpCode(str):
    """Custom bytecode."""

    def __init__(self, name, size) -> None:
        super().__init__()
        self.name = name
        self.size = size


custom_opcode = CustomOpCode("CUSTOM", 2)
dis.show_bytecode(custom_opcode)


# ── low-level C data structures and functions ──────────────────────────────────

print("\nctypes, struct, array:")
struct.Struct("?").size     # bool
array.array("h").itemsize   # signed short
array.array("H").itemsize   # unsigned short
array.array("i").itemsize   # signed integer
array.array("I").itemsize   # unsigned integer
array.array("l").itemsize   # signed long
array.array("L").itemsize   # unsigned long
array.array("q").itemsize   # signed quad
array.array("Q").itemsize   # unsigned quad

array.array("c").typecode

types.SimpleNamespace().addressof     # hex address of an instance
types.SimpleNamespace().memaddr       # exact physical address of an instance

# create a wacky type
wacky_type = types.new_class("WackyClass")()
wacky_type.addressof  # fails, as does memaddr

# get the type