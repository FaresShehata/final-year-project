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
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20

def positive_short_str(x) -> bool:
    return positive(x) and short_str(x)

class X(_Constrained):
    pass
X = Annotated[X, positive, short_str]

class Y(X): # type: ignore
    pass
Y = Annotated[Y, positive, short_str]

@Annotated["X", {"max": 10}]
def foo(x):
    pass
foo(-1)

# ── Annotated with a custom validator ────────────────────────────────────────

from typing_extensions import Annotated

A: Annotated[int, lambda n: True]
B: Annotated[int, lambda n: n == 10]

assert A == B
assert A != 10

# ── Annotated with multiple validators ───────────────────────────────────────

C: Annotated[int, lambda n: n >= 0, lambda n: n % 3 == 0]
D: Annotated[int, lambda n: n >= -100, lambda n: n % 7 == 0]

assert C == D == 12
assert C < 9
assert D <= -86
assert C + D == 24
assert C * D == 144

# ── TypedDict with no mandatory keys ─────────────────────────────────────────

MyDict: TypeAlias = TypedDict("MyDict", {str: str}, total=False)

my_dict = MyDict()
print(my_dict)

# ── TypedDict with non-optional keys ─────────────────────────────────────────

MyOtherDict: TypeAlias = TypedDict("MyOtherDict", {
    "id":      int,
    "email":   Annotated[str, "@"],
})

my_other_dict = MyOtherDict(id=1, email="user@example.com")
print(my_other_dict)

# ── TypedDict with default values ───────────────────────────────────────────-

MyDefaultDict: TypeAlias = TypedDict("MyDefaultDict", {
    "id":      int,
    "email":   str                  = "unknown@example.com",
})

my_default_dict = MyDefaultDict(id=1, email="user@example.com")
print(my_default_dict)

my_default_dict = MyDefaultDict(id=1, email="")
print(my_default_dict)

# ── Typing extras ───────────────────────────────────────────────────────────

from typing