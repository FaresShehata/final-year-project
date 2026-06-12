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
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    requests:   int


# ── ClassVars ────────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int; g: int; b: int; a: int = 255


class Settings(Generic[T]):
    default_value: T
    values: tuple[T, ...]
    
    def __init__(self, value: T) -> None:
        self.value = value
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={repr(self.value)}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value



# ── Typing Extras ────────────────────────────────────────────────────────────


def foo(x: Annotated[int, "foo", math.exp]) -> Annotated[float, "bar"]:
    ...


def add(a: Annotated[int, "a"], b: Annotated[int, "b"]) -> Annotated[int, "c"]:
    ...


def bar(t: Annotated[type[int], "t"]) -> Annotated[t, "u"]:
    ...


def baz(u: Annotated[U, "v"]) -> Annotated[V, "w"]:

    v: Annotated[V, "x"]
    w: Annotated[W, "y"]

    ...

    return w


# ── __class_getitem__ ────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)
V = TypeVar("V")


class C(Generic[T_co, V]): pass


C[C["X", "Y"], "Z"]


# ── __set_name__ ─────────────────────────────────────────────────────────────

class A(Generic[T]):
    def __init_subclass__(cls: type[A[T]]) -> None:
        assert cls.__annotations__["value"].__origin__ is list
        assert cls.__annotations__["value"].__args__[0].__origin__ is int
        super().__init_subclass__()
    

class B(A[list[int]]): pass


# ── __init_subclass__ ────────────────────────────────────────────────────────

class Parent:
    def __new__(cls, *args, **kwargs):
        print(f"Parent.__new__() called with args {args}, kwargs {kwargs}")
        return super().__new__(cls)


class Child(Parent):
    def __init_subclass__(cls, *args, **kwargs):
        print(
            f"Child.__init_subclass__() called with args {args}, kwargs {kwargs}"
        )
        super().__init_subclass__(*args, **kwargs)



# ── contextlib ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions, **kwds):
    try:
        yield
    except exceptions:
        pass


with suppress(FileNotFoundError, OSError):
    raise OSError()


@contextlib.redirect_stdout(io.StringIO())
def do_something():
    print(42)
    raise ValueError()

do_something()
print(do_something())


# ── numbers ABCs ────────────────────────────────────────────────────────────

for t in (float, int, complex):
    for n in (-3.5, -7, 0, 198, 1e-308, 1e308):
        print(f"{t(n)=}")

if not hasattr(numbers, "Number"):
    print(f"numbers.Number does not exist")

if not hasattr(numbers, "Real"):
           sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
