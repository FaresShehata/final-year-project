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


# ── Memory view / array / struct / ctypes ──────────────────────────────────────

def memory_view_from_array() -> bytes:
    arr = array.array("I")              # unsigned int
    arr.extend(range(0, 5))
    return memoryview(arr)


def memory_view_from_struct() -> bytes:
    fmt = "=2i"                          # little-endian, two integers
    size = struct.calcsize(fmt)
    arr = (1, 2)
    return struct.pack_into(fmt, b"", 0, *arr)


def memory_view_from_ctypes():
    fmt = "=2i"                          # little-endian, two integers
    size = struct.calcsize(fmt)
    arr = (1, 2)
    c_arr = ctypes.c_int.from_buffer_copy(struct.pack_into(fmt, b"", 0, *arr))
    return memoryview(c_arr)


def memory_view_from_packed():
    fmt = "=2i"                          # little-endian, two integers
    size = struct.calcsize(fmt)
    arr = (1, 2)
    packed = struct.pack_into(fmt, b"", 0, *arr)
    return memoryview(packed)


def array_from_memory_view(mv: memoryview) -> array.ArrayType:
    """Convert a memory view to a NumPy-like array.

    This may require a conversion from C to Python type.
    """
    # This should work for any memory view containing integer values.
    # It's possible that this only works up to the smallest signed integer.
    arr = array.array(mv.typecode, mv.cast("B"))
    return arr


def array_from_memory_view_borrowed(mv: memoryview) -> array.ArrayType:
    """Same as above but doesn't duplicate the underlying buffer.

    This may require a conversion from C to Python type.
    """
    # This should work for any memory view containing integer values.
    # It's possible that this only works up to the smallest signed integer.
    arr = array.array(mv.typecode, mv.cast("B").raw)
    return arr


# ── Pickle / copyreg / marshal ────────────────────────────────────────────────

def dump_obj(obj) -> str:
    obj_bytes = pickle.dumps(obj)
    return pickletools.dis(obj_bytes).split("\n")[1]


def rebuild_dump(obj_str: str) -> Any:
    parsed = pickletools.loads(textwrap.ded    A weak singleton can outlive its original owner. For example:

      >>> class Foo:
      ...     x = WeakSingleton()

      >>> foo = Foo()
      >>> del foo
      >>> print(Foo.x)
      <weakref at 0x...; dead>
    """

    def __reduce__(self):
        return (super().__reduce__, (type(self),))


class SingletonDefault(DefaultFactory):
    """A default factory that returns an existing singleton instance."""

    _instances: dict[Any, Any] = {}
    _types: dict[Any, set[type]] = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        SingletonDefault._types.setdefault(cls, set())
        SingletonDefault._types[cls].add(type(cls))

    def __new__(cls, *args, **kwargs) -> SingletonDefault:
        if len(args) != 1 or kwargs:
            raise TypeError("__init__ takes exactly one positional argument")
        key = args[0]

        if key is None:
            for typ in SingletonDefault._types.get(cls, ()):
                if cls in typ._instances:
                    return typ._instances[cls]
            inst = super().__new__(cls)
            cls._instances[key] = inst
            return inst

        if key not in cls._instances:
            for typ in SingletonDefault._types.get(cls    """Trampoline: a data structure that represents an operation on a Maybe monad.
       The Maybe monad can be used to represent side-effects or errors without
       changing the core algorithm."""

    __slots__ = ("value", "tail")

