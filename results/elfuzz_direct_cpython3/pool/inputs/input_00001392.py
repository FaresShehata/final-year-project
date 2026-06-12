"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(f"Got {val!r}, which exceeds range ({self.hi})")
        else:
            setattr(obj, self.priv, val)

    def __delete__(self, obj):
        delattr(obj, self.priv)

# ── Metaclass ────────────────────────────────────────────────────────────────

class Meta(type):
    """metaclass adds a new magic method to the class's namespace."""

    @property
    def MAGIC_METHOD(cls) -> str:
        return "__magic_method__"


class MagicMethod(metaclass=Meta):
    pass

MagicMethod.MAGIC_METHOD()


# ── Functions ────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def timer():
    start_time = time.perf_counter()
    yield
    print(f"Elapsed: {(time.perf_counter() - start_time):.3g}s")


# ── Generators ───────────────────────────────────────────────────────────────

class DigitsGenerator:
    """Generates all digits from 0 to n inclusive."""

    def __init__(self, n: int) -> None:
        self.n = n + 1
        self.i = 0

    def __iter__(self) -> Generator[int, int, None]:
        while self.i < self.n:
            yield self.i
            self.i += 1

DIGITS = DigitsGenerator(25)


# ── Decorators ───────────────────────────────────────────────────────────────

def accepts(*types):
    """
    Decorator that validates argument types.

    The decorator takes an arbitrary number of types as arguments. Each argument
    specifies what kind of object can be passed to the decorated function. If
    any of the given types doesn't match with the actual argument, raises a
    TypeError exception.
    """

    def inner(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            argspec = inspect.getfullargspec(func)

            if len(args) != len(argspec.args) - len(argspec.defaults or []):
                raise TypeError(f"{func.__qualname__}() takes "
                                f"{len(argspec.args) - len(argspec.defaults)} "
                                f"positional arguments but {len(args)} were given")

            for arg, tp in zip(args, argspec.annotations.values()):
                if arg is not Ellipsis and not isinstance(arg, tp):
                    raise TypeError(f"{arg!          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
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
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


class Positive(_Constrained): pass
class NonNegative(_Constrained): pass


# ── Annotated constraints (compile-time checked via type hint) ────────────────

class NoDataError(ValueError):
    pass



@overload
def count_if(predicate: Predicate[T]) -> Callable[[Iterable[T]], int]:
    ...


@overload
def count_if(predicate: Predicate[Any]) -> Callable[[Iterable[Any]], int]:
    ...


def count_if(predicate: Predicate[Any]):
    # Type checks are only performed at runtime.
    if not callable(predicate):
        raise TypeError(f"{predicate!r} must be a callable predicate")

    def count(source: Iterable[Any]) -> int:
        cnt = 0
        for x in source:
            if predicate(x):
                cnt += 1
        return cnt

    return count


# ── Context manager checks ───────────────────────────────────────────────────

class TextIO(io.TextIOWrapper):
    def __enter__(self):
        assert self.closed, "file already closed"
        return super().__enter__()

    def close(self):
        assert not self.closed, "file already closed"
        try:
            super().close()
        finally:
            self.closed = True


# ── Type variables ───────────────────────────────────────────────────────────

A: TypeVar("A")
B: TypeVar("B", bound=int)


class AClass:
    x: A


class BClass:
    y: B


# ── Union types ──────────────────────────────────────────────────────────────

Union[A, B]: TypeVar("Union", A, B)


