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

def example_typeddict() -> None:
    class Foo(TypedDict):
        bar: int
        baz: str

    f: Foo = {"bar": 123, "baz": "abc"}


def example_concatenate() -> None:
    class A:
        def do_something(self) -> str:
            return "A"

    class B:
        def do_something_else(self) -> str:
            return "B"

    class Foo(Generic[T], A):
        pass

    class Bar(Foo[B]):
        pass

    a: Foo[str] = Foo()
    assert a.do_something() == "A"


def example_annotated() -> None:
    class Foo(anio.Annotated[int]): ...
    class Bar(anio.Annotated[foo.Foo]): ...


anio: TypeAlias = Annotated


# ── Contextlib ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def example_contextmanager() -> tuple[int, list[int]]:
    yield 123, [456]


with example_contextmanager():
    print(reveal_type("ctx")) # type: ignore[arg-type]
    assert ctx == (123, [456])


@contextlib.contextmanager
async def example_async_contextmanager(x: int) -> AsyncIterator[int]:
    y: int = x * 10
    async with aio.Lock() as lock:
        try:
            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            raise ValueError(f"{x} is cancelled") from None
    yield y
    assert isinstance(y, int)


try:
    async for i in example_async_contextmanager(123):
        print(i)
except ValueError as e:
    print(e)
else:
    assert False



# ── Numbers (Abstract Base Classes) ──────────────────────────────────────────-

from decimal import Decimal
from fractions import Fraction
from math import inf, nan, pi, tau
from operator import truediv
from numbers import Number, Real, Integral, Complex, Rational
from numbers import Number, Rational, Integral, Complex, Real
from re import Pattern
from re import compile
from types import TracebackType
from typing import Awaitable, Iterator, Optional, Union
from typing_extensions import SupportsIndex, SupportsFloat

def example_numbers() -> None:
    assert isinstance(pi, Real)
    assert isinstance(tau, Real)
    assert isinstance(Decimal('2'), Real)
    assert isinstance(Fraction(1, 2), Real)
    assert isinstance(inf, Real)
    assert isinstance(-inf, Real)
    assert isinstance(nan, Real)
    assert isinstance(truediv, SupportsFloat)
    
    assert isinstance(int(1.5), Integral)
    assert isinstance(float(1), Integral)

    assert isinstance(complex(1j), Complex)
    assert isinstance(complex(1 + 2j), Complex)
    assert isinstance(True.real, Real)

    assert isinstance(bool(1), Real)
    assert isinstance(False, Real)
    assert isinstance(bool(), Real)
    assert isinstance(not 0, Real)
    assert isinstance(not -0, Real)
    assert isinstance(not 0.0, Real)
    assert isinstance(not 0.0 + 0.0j, Real)

    assert isinstance(None, NoneMeta)
    assert isinstance(None, bool)
    assert isinstance(None, int)
    assert isinstance(None, float)
    assert isinstance(None, complex)
    assert isinstance(object(), Any)
    assert isinstance(isinstance, SupportsTracebackType)


# ── pathlib ──────────────────────────────────────────────────────────────────


# ── TemporaryDirectory ───────────────────────────────────────────────────────


# ── TemporaryFile ────────────────────────────────────────────────────────────


# ── CsvFile ─────────────────────────────────────────────────────────────────


# ── Base64 ──────────────────────────────────────────────────────────────────


# ── Hashlib ──────────────────────────────────────────────────────────────────


# ── Hmac ────────────────────────────────────────────────────────────────────


# ── Secrets ──────────────────────────────────────────────────────────────────


# ── TextWrapper ──────────────────────────────────────────────────────────────


# ─import pathlib
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
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    assert isinstance(value, constraint), \
                        f"{self.pub}: {value!r} does not satisfy `{constraint}`"
        setattr(obj, self.priv, value)


def positive_integer(_: Annotated[int, Predicate(lambda x: x > 0)]):
    return _


def non_negative_float(_: Annotated[float, Predicate(lambda x: x >= 0)]):
    return _

def no_duplicates(
    _: Annotated[list[Any], 
              Predicate(lambda l: len(l) == len(set(l)))]
) -> list[Any]:
    return _


def zero_or_more(_: Annotated[list[Any], Predicate(lambda x: len(x) <= 1)]):
    return _


def one(_: Annotated[Any, Predicate(lambda x: x is True)]) -> bool:
    return _
    

# ── TypedDict ────────────────────────────────────────────────────────────────

class FooBarNumba(NamedTuple):
    a:  int
    b:  float
    c:  str
    d:  bytes
    e:  complex
    f:  tuple[int, ...]
    g:  list[float]
    h:  set[str]
    i:  frozenset[int]
    j:  range
    k:  memoryview
    l:  object
    m:  type


# ── Empty Tuple ──────────────────────────────────────────────────────────────


# ── ClassGetItem ────────────────────────────────────────────────────────────


# ── UserClass ────────────────────────────────────────────────────────────────


# ── Setter ──────────────────────────────────────────────────────────────────


# ── RevealType ───────────────────────────────────────────────────────────────


# ── Task ────────────────────────────────────────────────────────────────────


# ── ReusableTask ────────────────────────────────────────────────────────────


