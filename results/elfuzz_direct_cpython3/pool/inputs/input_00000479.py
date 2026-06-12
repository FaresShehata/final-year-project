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
        ann   = hints.get(self.pub) or hints.get(self.priv)
        if not isinstance(ann, type(None)):
            if not isinstance(value, ann):
                raise TypeError(f"{obj!r}.{self.pub!r} expected {repr(ann)}, got {value}")
        setattr(obj, self.priv, value)


def constrained(*types) -> type[_Constrained]:
    """Decorator for validating an attribute's type."""
    class Constrained(_Constrained):
        pass
    return Constrained


# ── get_type_hints() and reveal_type() stubs ─────────────────────────────────

reveal_type(__file__)
reveal_type(__annotations__)

if False:
    from mypy_extensions import TypedDict  # noqa:F401
else:
    class Foo(TypedDict):
        a: int
        b: str


# ── __class_getitem__ ────────────────────────────────────────────────────────

class A(Generic[T]):
    @classmethod
    def __class_getitem__(cls, params: tuple[T]) -> A[T]:
        ...


# ── __set_name__() ──────────────────────────────────────────────────────────


class B:

    def __set_name__(self, owner, name):
        self.name = name
        print(owner, name)


b = B()
print(b.name)


# ── __init_subclass__() ──────────────────────────────────────────────────────


class C:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        ...


C()


# ── contextlib ───────────────────────────────────────────────────────────────


@contextlib.contextmanager
def timer():
    start_time = time.time()
    yield lambda: time.time() - start_time
    print('Elapsed:', end=' ')
    print(timer())


with timer() as elapsed:
    time.sleep(3.5)
    print(elapsed())


# ── numbers ─────────────────────────────────────────────────────────────────


x = 123_456_789
assert x // 1 == x
assert x % 1 != 0
assert not isinstance(x, numbers.Real)
assert isinstance(x, numbers.Integral)
assert isinstance(x, numbers.Number)

y = 1.23e+15 + 1j*1.23