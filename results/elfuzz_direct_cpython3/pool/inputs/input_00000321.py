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

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyList(list):
    items_per_line: ClassVar[int] = 3
    item_separator: ClassVar[str] = ", "

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyClass:
    attribute_1: ClassVar[str] = "Hello"
    attribute_2: ClassVar[str] = "World"

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyString(str):
    def upper_case(self) -> str:
        return self.upper()

# ── VarArg and Kwarg ─────────────────────────────────────────────────────────

def var_arg_func(*args: Any) -> None:
    print(args)
    for arg in args:
        print(arg.__class__.__name__)

var_arg_func()
var_arg_func(1)
var_arg_func(True)
var_arg_func([1, 2])
var_arg_func(MyClass())
var_arg_func(MyString("abc"))

def kwarg_func(**kwds: Any) -> None:
    print(kwds)
    for key, val in kwds.items():
        print(key, val.__class__.__name__)

kwarg_func()
kwarg_func(name="Alice", age=30)
kwarg_func(person={"name": "Bob", "age": 25})
kwarg_func(items=[1, 2, 3])

# ── overload --- (Optional[Tuple[Any, ...]]) ─────────────────────────────────

from typing import overload

@overload
def my_function(param: tuple[int, str]) -> str: ...
@overload
def my_function(param: tuple[int, ...]) -> int: ...

def my_function(param: tuple[int, ...]) -> int:
    return sum(param)

my_tuple = (1, 2, 3)
print(my_function(my_tuple))

# ── Annotated ────────────────────────────────────────────────────────────────

def validate_string(value):
    try:
        repr(value)
    except:
        raise ValueError(f"{value!r} cannot be represented as a string")


def initialize(obj, cls, **kwargs):
    for attr, value in kwargs.items():
        if hasattr(cls, attr):
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>                        raise ValueError(f"{self.pub}={value!r} fails constraint")
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
