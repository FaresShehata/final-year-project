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


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __repr__(self) -> str:
        n, u = divmod(self.reading, 1)
        m, s = divmod(n, 60)
        h, t = divmod(m, 60)
        return f'{h} hours {t:.3f}s'

# ── ParamSpec ────────────────────────────────────────────────────────────────

def concat[T](x: T, y: T) -> tuple[T, ...]: return x, y

A = ParamSpec("A")
B = ParamSpec("B")


# ── TypeVar ─────────────────────────────────────────────────────────────────

Tm = TypeVar("Tm", bound=numbers.Integral)
Ts = TypeVar("Ts", int, float)
Tu = TypeVar("Tu", covariant=bool)
Tv = TypeVar("Tv", contravariant=bool)

def add(a:Tm, b:Tm) -> Tm: return a + b

class BoundedInt(int):
    @property
    def max(self) -> int: return 99
    @max.setter
    def max(self, value:int): pass



# ── ClassVar ─────────────────────────────────────────────────────────────────

class StrMethodMixin:
    def method(self, *args, **kwargs):
        print(id(self))
        return super().method(*args, **kwargs)

StrObject = object()
MyStringClass = type(StrObject)

class MyString(MyStringClass, StrMethodMixin):

    def __str__(self) -> str:
        return 'abc'

print('instance', id(MyString()), MyString())

a = MyString()

print('func', id(str), str.__func__)

b = a.method()
c = str(a)

d = a.method()
e = str(b)

f = c == d
g = e == f


# ── Annotated ───────────────────────────────────────────────────────────────

@Annotated['list[int]', lambda _: _.all(lambda x: x < 10)]
def test_annotated(values: list[int]) -> None:
    assert all(v < 10 for v in values)



# ── get_type_hints ──────────────────────────────────────────────────────────

def func1(x,y:str) -> tuple[int,str]:
    return (1, y)

def func2(z:list[int], w:BoundedInt) -> tuple[BoundedInt,int]:
    return (w, z[-1])

def func3(p:A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z:tuple[list[int]] = ()) -> tuple[tuple[int,...],...]:
    return ((p[0][0][0][0][0][0]), *(q[-1] for q in p))

def func4(s:Any,*args,**kwargs) -> tuple[Any,...]:
    return (s,) + args + tuple(kwargs.values())

assert get_type_hints(func1)['y'] == str
assert get_type_hints(func2) == {'z': list[int], 'w': BoundedInt}
assert get_type_hints(func3).keys