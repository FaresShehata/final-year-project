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
dis.dis(compile("1 + 2", "test.py", "exec"))


def f(x):
    x = x * 2


f(5)
print(f.__code__)


def g():
    yield 3.14


g()
print(g().__code__)

# ── Disassembly of functions and methods ───────────────────────────────
x = 99
y = 88


def sum_two_numbers(a, b):
    return a + b


sum_two_numbers(1, 4)

sum_two_numbers.func_code.co_varnames
sum_two_numbers.func_closure
sum_two_numbers.func_defaults
sum_two_numbers.__annotations__

# ── Code object properties ────────────────────────────────────────────────
a = compile(
    "a = 1\nb = 2\nc = 3",
    "example.py",
    "exec",
)


print(repr(a))

print(
    """
    co_argcount:    {co_argcount}
    co_cellvars:    {cellvar}
    co_consts:      {const}
    co_filename:    {filename}
    co_firstlineno: {firstline}
    co_flags:       {flags}
    co_freevars:    {freevar}
    """.format(
        **{
            k: v
            for k, v in vars(a).items()
            if not k.startswith("_") or k == "_globals"
        }
    )
)

# ── Struct module ─────────────────────────────────────────────────────────────
struct.pack("<H", 123)
struct.unpack(">I", "\xff\xff\x00\x01")[0]
struct.pack(">HH", 123, 456)

# ── Array module ─────────────────────────────────────────────────────────────
array.array("h", (1, 2, 3))
array.array("i", [1, 2, 3])

# ── Memoryview ───────────────────────────────────────────────────────────────
memoryview(b"abc")
memoryview([1, 2, 3])
memoryview(array.array("B", (1, 2, 3)))

m = memoryview(b"\x00\x7f\xfe\xff")
m[0]
m[-1]

m.strides
m.suboffsets
m.readonly

m.cast("S")

byteorder = m