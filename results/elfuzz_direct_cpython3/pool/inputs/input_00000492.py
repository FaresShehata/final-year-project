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
    co = co.replace(name=new_name)
    fn_new = types.FunctionType(co, fn.__globals__, name=new_name, fn.__defaults__, fn.__closure__)
    return fn_new


def rename_code(obj: object, old_name: str, new_name: str) -> None:
    """Rename the name attribute and source filename of an imported module."""
    if isinstance(obj, types.ModuleType):
        obj.__dict__["__name__"] = new_name             # set name first
        obj.__file__ = obj.__file__[:-len(old_name)]    # then change file
    elif hasattr(obj, "__module__"):
        rename_code(getattr(sys.modules[obj.__module__], old_name), old_name, new_name)
        setattr(obj, "__module__", f"{obj.__module__}.{new_name}")  # type: ignore[attr-defined]
    elif hasattr(obj, "__class__") and issubclass(obj.__class__, importlib.abc.MetaPathFinder):  # type: ignore[attr-defined]
        if hasattr(obj, "__path__"):                         # type: ignore[attr-defined]
            for path in obj.__path__:                        # type: ignore[attr-defined]
                rename_code(path, old_name, new_name)        # type: ignore[attr-defined]
        for finder in getattr(obj, "__finder__", []):        # type: ignore[attr-defined]
            if not isinstance(finder, importlib.machinery.PathFinder):  # type: ignore[attr-defined]
                continue
            modules = getattr(finder, "_modules", {})       # type: ignore[attr-defined]
            if old_name in modules:
                modules[new_name] = modules.pop(old_name)   # type: ignore[attr-defined]
    else:
        raise TypeError(f"can't rename {type(obj).__qualname__!r} instances")


def replace_import(obj: object, old_name: str, new_name: str) -> None:
    """Replace an import's name after importing it."""
    if isinstance(obj, types.ModuleType):
        del sys.modules[f"{old_name}.sys"]
        sys.modules[new_name] = sys.modules.pop(old_name)  # type: ignore[attr-defined]
    elif hasattr(obj, "__module__") and obj.__module__.startswith(old_name):
        new_module = obj.__module__[len(old_name)+1:]
        del sys.modules[f"{old_name}.sys"]
        sys.modules[new_module] = sys.modules.pop(f"{old_name}.sys")  # type:Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total
    acc._init_value = init  # type: ignore[attr-defined]
    return acc


def make_peepers():
    peepers = []
    for i in range(3):
        peeper = make_accumulator(i+1)
        peepers.append(peeper)
    return peepers


# ── Decorators ────────────────────────────────────────────────────────────────

def trace(func: Callable):
    @functools.wraps(func)
    def traced_func(*args, **kwargs):
        print("->", func.__name__, "(", args, kwargs, ") → ")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise e from None
        else:
            print("<-", result)
            return result
    return traced_func


# ── Higher-order functions & lambdas ──────────────────────────────────────────

def map_iter(iterable: Iterable[A], fn: Callable[[A], B]) -> Iterator[B]:
    for item in iterable:
        yield fn(item)


def map_list(xs: list[A], fn: Callable[[A], B]) -> list[B]:
    return [fn(x) for x in xs]


def filter_iter(iterable: Iterable[A], pred: Callable[[A], bool]) -> Iterator[A]:
    for item in iterable:
        if pred(item):
            yield item


