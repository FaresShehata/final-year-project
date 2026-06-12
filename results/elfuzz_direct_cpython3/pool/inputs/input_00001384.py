"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float

# ── TypedDict ────────────────────────────────────────────────────────────────
JsonArray: TypeAlias = "[JsonObject]" | "[JsonValue]"
JsonObject: TypeAlias = "{str: JsonValue}"

# ── Class variables ──────────────────────────────────────────────────────────

class Person(NamedTuple):
    name: str                 # required
    age: int                  # optional, default value is used
    email: str | None         # optional, 'None' will be assigned when missing


class Point(NamedTuple):
    x: int                    # required
    y: int                    # required
    z: int | None             # optional, 'None' will be assigned when missing


class Vector(NamedTuple):
    x: int                    # required
    y: int                    # required
    z: int | None             # optional, 'None' will be assigned when missing


class Box(NamedTuple):
    length: int               # required
    height: int               # required
    width: int | None         # optional, 'None' will be assigned when missing


# ── Inheritance ───────────────────────────────────────────────────────────────

class Rectangle(Point, Vector):

    def area(self):
        return self.x * self.y

    def perimeter(self):
        return 2*self.x + 2*self.y

    def diagonal(self):
        return math.sqrt((self.x - self.z)**2 + (self.y - self.z)**2)


class Cube(Box, Rectangle):  # Multiple inheritance allowed

    def surface_area(self):
        return 6 * self.area()

    def volume(self):
        return self.length * self.height * self.width


class SpaceShip(Rectangle):  # Single inheritance not supported by most languages

    def __repr__(self):
        return f"<SpaceShip {tuple(self)!r}>"

    def __contains__(self, item):
        if isinstance(item, numbers.Real):
            return False
        elif hasattr(item, "__iter__"):
            item = tuple(item)
        else:
            raise TypeError("Can only check containment against tuples.")
        return all(v == i for v, i in zip(self, item))


# ── Generics ─────────────────────────────────────────────────────────────────

class List[T](list[T]):
    pass


class Dict[K, V](dict[K, V]):
    pass


class Set[S](set[S]):
    pass


class FrozenSet[F](frozenset[F]):
    pass


class Tuple[TupleType, *Rest](tuple[TupleB = TypeVar("B")
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

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapped_fn(*args, **kwargs):
        key = args, frozenset(kwargs.items())
        if key in cache:
            return cache[key]
        result = fn(*args, **kwargs)
        if isinstance(result, tuple):
            val, next_ = result
            cache[key] = (val, lambda new_args, new_kwargs: wrapped_fn(
                *next_(new_args), **{**kwargs, **new_kwargs},
            ))
        else:
            cache[key] = result
        return result
    return wrapped_fn



# ── Higher-order functions & combinators ───────────────────────────────────────

def identity(x: A) -> A:
    return x


def invoker(funcs: list[Callable]) -> Callable[..., Any]:
    """Invoker combinator, creates a callable from a list of function arguments.

    >>> invoker([lambda x: x+1])(5)
    6
    """
    def invoked(*args, **kwargs):
        results = map(lambda func: func(*args, **kwargs), funcs)
        return sum(results, start=identity)
    return invoked


def compose2(f: Callable, g: Callable) -> Callable:
