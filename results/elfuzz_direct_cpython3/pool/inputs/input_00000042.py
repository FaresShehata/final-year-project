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


# ── __class_getitem__

class BarMeta(type):

    def __getitem__(cls, item: str | tuple[str, ...]) -> Bar:

        class Foo(metaclass=BarMeta):
            pass
        
        return cls(Foo)


class Bar(metaclass=BarMeta): ...
    

class Baz(Annotated["Foo"[_], "key"]): ...


# ── __set_name__

class Foo:
    def __init__(self, x: Annotated[int, "__set_name__() called on me with {x=}"]):
        ...


class Bar(Foo):
    x = 3.14
    

# ── __init_subclass__


class BaseClass:

    def __init_subclass__(
        cls, 
        foo: Annotated[int, "I am the docstring of my subclass"],
        **kwargs: dict[str, Any],
    ) -> None:
        print(kwargs)
        

class Subclass(BaseClass, foo="This is a parameter"):

    def __str__(self) -> str:
        return f"{type(self).__name__}(foo={self.foo})"


# ── contextlib

@contextlib.contextmanager
def suppress(*exceptions: Exception) -> Generator[None, None, None]:
    try        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
