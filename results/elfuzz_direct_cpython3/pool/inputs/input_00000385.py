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
            for param, constraint in ann.__metadata__["constraints"]:
                if not constraint(value):
                    raise TypeError(f'{obj.type}.{self.pub} must satisfy "{constraint}"')
        setattr(obj, self.priv, value)

    def __delete__(self, obj):
        delattr(obj, self.priv)

# ── Constrained types ─────────────────────────────────────────────────────────

positive: TypeAlias = Annotated[int, Predicate(lambda n: n >= 0)]
short_str: TypeAlias = Annotated[str, Predicate(lambda s: len(s) <= 20)]

# ── Context managers ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exc_types) -> Generator[None, None, None]:
    with contextlib.suppress(*exc_types):
        yield

@contextlib.contextmanager
def redirect_stdout(file: io.IOBase):
    old = sys.stdout
    sys.stdout = file
    try:
        yield file
    finally:
        sys.stdout = old

@contextlib.contextmanager
class TimeoutError(Exception): pass

@contextlib.contextmanager
def timeout(seconds: Seconds):
    timer = threading.Timer(seconds, lambda :raise_timeout())
    timer.start()
    try:
        yield
    finally:
        timer.cancel()

def raise_timeout():
    raise TimeoutError()


# ── Numbers abstract base class ────────────────────────────────────────────────

class Number(numbers.Number):
    @property
    def is_integer(self) -> bool:
        return False

    def __truediv__(self, other):
        return Fraction(self, other)

class Rational(Number):
    __slots__ = ("numerator", "denominator")

    def __init__(self, numerator=1, denominator=1):
        self.numerator  = numerator
        self.denominator = denominator

    def __add__(self, other):
        return self + other

    def __mul__(self, other):
        return self * other

    def __sub__(self, other):
        return self - other

    def __floordiv__(self, other):
        return self // other

    def __mod__(self, other):
        return self % other

# ── Pathlib ───────────────────────────────────────────────────────────────────

path = pathlib.Path(__file__)
relative_path = path.relative_to(path.parent)

with path.open(encoding="utf-8") as input_file:
    output_text = path.read_text    return isinstance(x, (int, float)) and x > 0

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
        return max((self.end, other.end) - min((self.start, other.start)))


# ── Text formatting ───────────────────────────────────────────────────────────

class Formatter(string.Formatter):
    def format_field(self, value, spec):
        try:
            return super().format_field(value, spec)
        except (TypeError, AttributeError):
            return repr(value)


print(Formatter().vformat("{a} {b}", [], {"a": 3.14, "b": "π"}))


# ── String tokenization ───────────────────────────────────────────────────────

input_string = 'Hello world'
tokens = list(tokenize.generate_tokens(io.StringIO(input_string).readline))

for token in tokens:
