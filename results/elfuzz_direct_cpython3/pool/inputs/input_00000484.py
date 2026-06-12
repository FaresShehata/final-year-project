"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import enum
import inspect
import itertools as it
import math
import os
import platform
import random
import re
import struct
import sys
import timeit
import types
import typesupport
import typing
import weakref

import numpy as np
import numpy.typing as npt

try:
    import tracemalloc
except ImportError:
    tracemalloc = False

if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, List, NoReturn, Optional, Tuple, TypeVar, Union

    Any = typing.Any
    Callable_T = TypeVar("Callable_T", bound=types.FunctionType)

else:                                # no typing
    from builtins import *

    class Callable_T(Callable):
        pass


# ── Functions to test ─────────────────────────────────────────────────────────

def identity(x: Any) -> Any:
    return x


def square(x: float) -> float:
    return x ** 2


def hypot(x: float, y: float) -> float:
    return math.hypot(x, y)


def fibonacci(n: int) -> int:
    a, b = 0, 1
    while n > 0:
        yield a
        a, b = b, a + b
        n -= 1


def pi_digits(limit: int) -> Generator[int, None, None]:
    k = 0
    d = 46
    p = 10**d
    while limit > 0:
        q = (p * 25) // (a := 3 - a)
        s = (q * 9) // (b := 7 - b)
        r = ((p * s) // b + (q * 3)) // (c := 17 - c)
        yield r
        k += c
        p *= 10**(d-c)
        d += 1
        n <<= 1
        limit -= 1


def chop_and_divide(a: int, b: int, *, threshold: int = 1_000_000) -> int | float:
    # https://www.joelonsoftware.com/2002/11/25/follow-up/
    if abs(b) < threshold:
        return a / b
    return chop_and_divide(a // b, b // b, threshold=threshold) + a % b // b


def log10(x: float, *, epsilon: float = 1e-5) -> float:
    """Natural logarithm of x using Taylor series approximation."""
    z = 0.0
    e = 0.5
    while True:
        y = 10**z * e - x
        if abs(y) <= epsilon:
            break
        z += y    return round(float(value), ndigits=ndigits)


def get_random_seed(seed=None) -> int:
    """Get a deterministic (and reproducible) seed for use with random.random()."""
    if seed is None:
        seed = int(time.time())
    assert seed >= 0, "seed must be non-negative"
    return seed


# ── low-level Python: bytecode intros
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
