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
    errors:      int
    count:       int


# ── Annotated ────────────────────────────────────────────────────────────────

Annotated[int, "foo"] + Annotated[int, "bar"]
"""A union of two annotated types."""


# ── get_type_hints ───────────────────────────────────────────────────────────

TypeH: TypeAlias = tuple[tuple[str, ...], dict[str, type]]
for t in [get_type_hints(lambda a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z : True)]:
    assert t is not None and len(t) == 2
    assert isinstance(t[0], tuple)
    assert all(isinstance(k, str) for k in t[0])
    assert isinstance(t[1], dict)
    assert all(isinstance(k, str) for k in t[1])


# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(lambda a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z : True)


# ── functools.partial ────────────────────────────────────────────────────────

partial: Callable[..., object] = lambda *args,**kwargs: None


# ── contextlib.suppress ─────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions: Exception) -> Generator[Never, Never, Never]:
    yield


# ── Context Manager ──────────────────────────────────────────────────────────

class MyContextManager(object): pass
with contextlib.redirect_stdout(io.StringIO()) as cm: pass


# ── abc.ABCMeta.__subclasscheck__() ──────────────────────────────────────────

assert abc.ABCMeta.__subclasscheck__("abc", TestABC)


# ── abc.ABCMeta.__instancecheck__() ──────────────────────────────────────────

class BaseABC(abc.ABC): pass
BaseABC.__subclasshook__ = lambda cls, obj : False


class SubClass(BaseABC): pass
SubClass()
isinstance(SubClass(), BaseABC)


# ── abc.ABCMeta.register() vs. __subclasshook__ ──────────────────────────────

class MyDecorator(type):
    def __new__(cls, name, bases, dct): ...

    @classmethod
    def __prepare__(cls, name                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
