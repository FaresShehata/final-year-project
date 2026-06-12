"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
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
XOR   = lambda a: lambda b: NOT(AND(a)(b))
ID    = lambda x: x
K     = ID
I     = TRUE
Y     = lambda g: g(Y(g))


# ── Higher-Order Functions and Closures ───────────────────────────────────────

def add(x: A) -> Callable[[A], B]:
    def wrapper(y: A) -> B:
        return x + y
    return wrapper


def adder_factory() -> Callable[[A], Callable[[A], B]]:
    """Returns a factory function that returns an adder function when called."""

    def add_to(x: A) -> Callable[[A], B]:
        def add_y(y: A) -> B:
            return x + y
        return add_y
    return add_to


def compose(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    return lambda x: g(f(x))

compose_many = functools.reduce(compose)


# ── Iterators and Generators ─────────────────────────────────────────────────

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


FibonacciIterator: TypeAlias = Iterable[int]
fibonacci_iter = map(fibonacci, count())


def fibonacci_generator(n: int) -> Iterator[int]:
    for i in range(n):
        yield fibonacci(i)


def fibonacci_generator_2(n: int) -> Iterator[int]:
    fib_i_minus_1 = 1
    fib_i_minus_2 = 0
    for _ in range(n):
        yield fib_i_minus_1
        next_fib = fib_i_minus_1 + fib_i_minus_2
        fib_i_minus_2 = fib_i_minus_1
        fib_i_minus_1 = next_fib


# ── Currying and Partial Application ──────────────────────────────────────────

from typing_extensions import Concatenate
from functools import wraps
from inspect import signature

def curry(func: Callable[P, T]) -> Callable[..., Callable[P, T]]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Callable[P, T]:
        sig = signature(func)
        bound_func = sig.bind_partial(*args, **kwargs).arguments
        return lambda *more_args, **moreimport ast
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
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class Option(TypedDict):
    left: str
    right: str


class Line(NamedTuple):
    number: int
    line: str


class Event(NamedTuple):
    event_id: int
    timestamp: float
    message: str
    level: int


# ── Enumerations ──────────────────────────────────────────────────────────────

from enum import Enum, IntEnum, auto
import enum

SPEED: Final[int] = 90000
DIRTY: Final[bool] = True
MAGIC: Final[float] = 3.14159265358979323846264338327950288

# ── Classes ───────────────────────────────────────────────────────────────────

from abc                  import abstractmethod
from collections.abc      import Iterable
from dataclasses          import dataclass, field
from operator             import attrgetter, methodcaller
from pathlib              import Path
from pickle               import loads, dumps
from queue                import Queue
from re                   import compile, sub
from signal               import SIGINT, signal
from sys                  import exit, stderr
from types                import TracebackType
from typing               import (
