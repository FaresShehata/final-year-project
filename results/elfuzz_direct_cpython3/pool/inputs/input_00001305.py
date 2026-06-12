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
            raise AttributeError(name)
        val = getattr(obj, self.priv)
        for constraint in get_annotations(owner)[self.pub].values():
            assert isinstance(val, constraint), f"{val=} does not satisfy {constraint}"
        return val

    def __set__(self, obj, value):
        raise TypeError(f"'{self.pub}' attribute is read-only")


class Int(_Constrained):
    """Annotated[int]"""


class Str(_Constrained):
    """Annotated[str]"""


class Float(_Constrained):
    """Annotated[float]"""


class Predicate(_Constrained):
    def __set__(self, obj, value):
        if not callable(value):
            raise ValueError("Must be a callable predicate function.")
        super().__set__(obj, value)


class Enum(_Constrained):
    def __set__(self, obj, value):
        values = getattr(obj, self.pub)
        if value not in values.values():
            raise ValueError(
                f"{value} must be one of {', '.join(map(str, values.values()))}."
            )
        super().__set__(obj, value)


class Empty(_Constrained):
    pass


# ── ParamSpec ────────────────────────────────────────────────────────────────

A: TypeVar("A") = Annotated[int]
B: TypeVar("B", bound=int)
C: TypeVar("C", int, str)
D: TypeVar("D", int | str)
E: TypeVar("E", int | str | float)
F: TypeVar("F", int | str | float | bool)
G: TypeVar("G", int | str | float | bool | tuple[int])
H: TypeVar("H", int | str | float | bool | tuple[int] | tuple[str])


# ── ParamSpec use case ───────────────────────────────────────────────────────

def foo(a: A, b: B, c: C[D]):
    print(a, b, c)

foo(1, a="a", c=(1,))  # OK
foo(1, b="b", c=(1,))  # OK
foo(1, c=(1,))         # Error: "c" has type "tuple[int]", but was annotated with "tuple[int | str]".


# ── Union use case ──────────────────────────────────────────────────────────

X = TypeVar('X')
Y = TypeVar('Y')

Union[X, Y]


#
@contextlib.contextmanager
def redirect_stdout(out: io.StringIO):
    old = sys.stdout
    sys.stdout = out
    try:
        yield
    finally:
        sys.stdout = old


# ── Numbers ABIs ────────────────────────────────────────────────────────────

default_float_info = {
    "emax": 1023,
    "eps": 1e-9,
    "machep": -97,
    "minexp": -999,
    "mininvexp": -98,
    "minpos": 2.2250738585072014e-308,
    "max": 1.7976931348623157e+308,
    "maxexp": 1024,
    "precision": 15,
}


def new_float_info() -> dict[str, int]:
    info = default_float_info.copy()
    info["max"] *= 1.25**info["machep"]
    return info


class FloatInfo(new_float_info()):
    pass


f = FloatInfo(max=5.5)
print(f.max)


class FloatTypeInfo:
    max: int
