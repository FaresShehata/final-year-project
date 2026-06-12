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


def frame_depth() -> tuple[int, str]:
    """
    Return a tuple containing the number of frames on the stack and the name of the calling function.

    >>> from pprint import pprint as pp
    >>> def foo(): print("foo"); bar()
    >>> def bar(): print("bar")
    >>> def baz(): print("baz") foo(); bar(); baz()
    ...
    baz
    bar
    foo
    >>> pp(depth_probe())
    ['baz', 'bar', 'foo']
    >>> frame_depth()
    (3, 'foo')
    """
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return len(names[:-1]), names[-1]


# ── Ctypes: pointer arithmetic, memory allocation, pointers to members ──────────

def ctypes_pointer_arithmetic():
    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_float)]

    p = Point(7, 2.5)
    q = p + 1
    assert q.y == 6.5
    p.x = 9
    q = p + 2
    assert q.y == 4.5


def ctypes_memory_allocation():
    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_float)]
    p = Point(7, 2.5)

    ptr = ctypes.pointer(p)
    assert ptr.contents.x == 7
    assert ptr.contents.y == 2.5

    ptr.contents.x = 11
    ptr.contents.y = 4.5
    p = ptr.contents
    assert p.x == 11
    assert p.y == 4.5

    del ptr
    p = ptr.contents     # PyMem_Free(ptr); raise dangling pointer exception!
    assert p.x == 11
    assert p.y == 4.5


def ctypes_pointers_to_members():
    class Point(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_int32),
            ("y", ctypes.c_float),
            ("z", ctypes.POINTER(Point)),
        ]
    p = Point(7, 2.5, None)
    p.z = ctypes.pointer(p)
    assert p.z.contents.x ==     return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
