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


# ── Memory view & array manipulation ──────────────────────────────────────────

def arrays_and_memory_views() -> None:
    """Demonstrate how to create arrays and memory views of arbitrary types."""
    # Define some data using the standard C types we know about...
    c_int_packed = [-1, -2]
    c_float_packed = [5.5e-6, 9.7]
    c_double_packed = [math.pi, math.e]
    c_char_packed = ["a", "\x00"]

    # ...and use struct.pack to pack them into arrays.
    int_array = array.array("i")
    int_array.fromlist(c_int_packed)

    float_array = array.array("f")
    float_array.fromlist(c_float_packed)

    double_array = array.array("d")
    double_array.fromlist(c_double_packed)

    char_array = array.array("c")
    char_array.frombytes(bytes(c_char_packed))

    # Construct memory views on these arrays...
    int_view = memoryview(int_array)
    float_view = memoryview(float_array)
    double_view = memoryview(double_array)
    char_view = memoryview(char_array)

    print("<int>:", repr(int_view.tobytes()))
    print("<float>:", repr(float_view.tobytes()))
    print("<double>:", repr(double_view.tobytes()))
    print("<char>:", repr(char_view.tobytes()))

    # ...and use struct.unpack to unpack them back.
    print("<int>: ", end="")
    print(*struct.unpack(f">{len(int_array)}i", int_view))
    print("<float>: ", end="")
    print(*struct.unpack(f">{len(float_array)}f", float_view))
    print("<double>: ", end="")
    print(*struct.unpack(f">{len(double_array)}d", double_view))
    print("<char>: ", end="")
    print(*struct.unpack(f">{len(char_array)}c", char_view))


# ── Copying vs pickling ───────────────────────────────────────────────────────

def copy_and_pickle(obj) -> tuple[Any, bytes, dict[str, Any]]:
    """Copy an object and pickle it for future inspection.

    Return: obj itself, its binary representation, and a map of ids that changed.
    """
    ref = weakref.ref(obj)
    copied_obj = copy.deepcopy(ref())
    pkl_bytes = pickle.dumps(copied_obj)
    id_map:    def perimeter(self) -> float: ...

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

    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
