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
    co_new = co.replace(co_name=new_name)
    fn_new = types.FunctionType(
        co_new,
        globals(),
        name=new_name,
        argcount=len(co.co_varnames),
        nlocals=len(co.co_cellvars),
        stacksize=co.co_stacksize,
        flags=co.co_flags,
        lnotab=co.co_lnotab.copy(),
        consts=list(co.co_consts),
        names=co.co_names,
        varnames=co.co_varnames,
        filename=co.co_filename,
        name=None,           # remove the original name from the cloned function
        freevars=tuple(),    # cloning does not create any free variables
        cellvars=tuple(),     # cloning does not create any cell variables
    )
    fn_new.__defaults__ = tuple(None if v is None else v for v in co.co_defaults)   # noqa: E501
    fn_new.__kwdefaults__ = {k: v for k, v in zip(co.co_kwonlyargcount, co.co_varnames)}  # noqa: E701
    return fn_new


# ── Ctypes ───────────────────────────────────────────────────────────────────-

def print_cstruct(ctypes.Structure):

    print(f"\nClass {ctypes.Structure.__qualname__} at {id(ctypes.Structure)}")
    print(" - fields:")
    print("\n".join(f"  - {field.name}: {field.type_}" for field in ctypes.Structure._fields_))
    print("\n - methods:")


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


# ── Struct ────────────────────────────────────────────────────────────────────

def print_struct(array.array):

    print(f"\nClass {array.array.__qualname__} at {id(array.array)}")
    print(" - item size:", array.array.itemsize)
    print(" - buffer info:", array.array.buffer_info())
    print(" - dtype:", array.array.dtype)
    print(" - data:", array.array.data)
    print(" - format string:", array.array.format)
    print(" - typecode:", array.array.typecode)


class Point(array.array):
    _typecode_ = 'i'  # use this to make array.Point behave like array.array('i')
    _typedocs_ = {"itemsize": 4}


# ── Array ────────────────────────────────────────────────────────────────────

def print_array(array.array):

    print(f"\nClass {array.array.__qualname__} at {id(array.array)}")
    print(" - item size:", array.array.itemsize)
    print(" - datatype:", array.array.datatype)
    print(" - data:", array.array.data)
    print(" - format string:", array.array.format)
    print(" - typecode:", array.array.typecode)


class Point(array.array):
    _typecode_ = 'i'
    _typedocs_ = {"datatype": "int"}
    _typecheck_ = lambda self, value: isinstance(value, int    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def area(self) -> float:
        return math.pi * (self.radius**2)

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

    def __str__(self) -> str:
        return f"Circle(radius={self.radius:.3g})"


class Rectangle(Shape):
