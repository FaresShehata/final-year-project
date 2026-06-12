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
        assert isinstance(value, self.expected), \
               f"{obj!r}.annotated_value must be {self.expected}"
        setattr(obj, self.priv, value)


class NonEmpty(str): pass
class Positive(int): pass
class ZeroOrMore(int): pass
class Integer(Annotated[int, NonEmpty]):
    expected = NonEmpty
NonEmptyInteger = Integer
PositiveInt = Integer[Positive]
ZeroOrMoreInt = Integer[ZeroOrMore]

# ── Annotated with type aliases (for type hinting only) ──────────────────────

@typing.overload
def annotated(typ: TypeAlias, *args, **kwargs):
    ...

@typing.overload
def annotated(
    typ: TypeAlias, *args, **kwargs) -> TypeAlias:
    ...

def annotated(typ: TypeAlias, *args, **kwargs):
    if len(args) == 0 and len(kwargs) == 0:
        # no arguments
        return Annotated[typ, ()]
    elif len(args) == 0:
        # just a single constraint specified
        return Annotated[typ, (args[0],)]
    else:
        # multiple constraints specified
        return Annotated[typ, tuple(args + kwargs.values())]


# ── get_type_hints ──────────────────────────────────────────────────────────

def my_get_type_hints(name: str) -> dict[str, type]:
    hints = get_type_hints(my_func, localns={"my_func": globals()[name]})
    return {
        k: t for k, t in hints.items()
        if not isinstance(t, TypeGuardType) and not isinstance(t, TypeStubType)
    }


# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(my_var)


# ── Context managers ────────────────────────────────────────────────────────

with suppress(Exception):
    print("This will never raise an exception!")

print(flush=True)


@contextlib.contextmanager
def suppress(*exceptions: type[BaseException]) -> Iterator[None]:
    try:
        yield
    except exceptions:
        pass


# ── pathlib ─────────────────────────────────────────────────────────────────

pathlib.Path.home()

p = pathlib.Path("/tmp").expanduser() / "foo.txt"
p.exists()


# ── Temporary files ─────────────────────────────────────────────────────────

tempfile.NamedTemporaryFile(mode="w+", delete=False).close()

tfd = tempfile.TemporaryDirectory(dir="/tmp", prefix="test_", suffix=".txt")
print(tfd.name)
tfd.cleanup()


# ── Context manager with explicit context exit ───────────────────────────────

with open("/dev/null") as devnull:
    devnull.write("hello world")


# ── Numbers abstract base class ──────────────────────────────────────────────

assert isinstance(2**63 - 1, numbers.Integral)
assert isinstance(2.718281828459045, numbers.Rational)
assert isinstance(-0.000000000000001, numbers.Real)
assert isinstance(True,

def pred(n: int) -> int:
    """Predessor function."""
    n -= 1
    return n


def add(m: int, n: int) -> int:
    """Church addition."""
    m = int(m)
    n = int(n)

    def _add(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = succ(result)
            m = pred(m)
        while n > 0:
            result = succ(result)
            n = pred(n)
        return result
    return _add


def mul(n: int, m: int) -> int:
    """Church multiplication."""
    m = int(m)
    n = int(n)

    def _mul(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = add(result, n)
            m = pred(m)
        return result
    return _mul


def inc(n: int) -> int:
    """Church increment."""
    return add(1, n)


def dec(n: int) -> int:
    """Church decrement."""
    return sub