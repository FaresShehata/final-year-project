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
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return super().__truediv__(other)
        elif isinstance(other, numbers.Integral):
            return Fraction(self.numerator * other.denominator + self.denominator * other.numerator, self.denominator * other.denominator).limit_denominator()
        else:
            raise TypeError("'/' not supported between instances of 'Rational' and '{other}'")


class Complex(numbers.Complex):
    def conjugate(self):
        return complex(*self.real, -self.imag)


class IrrationalError(Exception):
    pass

class Irrational(numbers.Number):
    _is_irrational = True

    @classmethod
    def from_float(cls, val):
        try:
            return cls(val)
        except OverflowError:
            raise IrrationalError(str(val))

    @property
    def real(self):
        raise NotImplementedError()

    @property
    def imag(self):
        raise NotImplementedError()


class Algebraic(numbers.Real):
    @classmethod
    def from_integer(cls, val):
        try:
            return cls(val)
        except OverflowError:
            raise ValueError(f"'{val}' cannot be converted to an algebraic integer")


class AlgebraicInteger(numbers.Complex):
    @classmethod
    def from_float(cls, val):
        try:
            return cls(val)
        except OverflowError:
            raise ValueError(f"'{val}' cannot be converted to a floating point number")


class Real(numbers.Number):
    @classmethod
    def from_integer(cls, val):
        try:
            return cls(val)
        except OverflowError:
            raise ValueError(f"'{val}' cannot be converted to a real number")

    @classmethod
    def from_real(cls, val):
        try:
            return cls(float(val))
        except ValueError:
            return float(val)

    @property
    def real(self):
        return self

    @property
    def imag(self):
        return 0.0

    def conjugate(self):
        return self


class AlgebraicReal(numbers.Complex):
    @classmethod
    def from_float(cls, val):
        try:
            return cls(val)
        except OverflowError:
            raise ValueError(f"'{val}' cannot be converted to an algebraic real number")

    @property
    def real(self):
        return self

    @property
    def imag(self):
        return 0.0

    def conjugate(self):
        return self


class Algebra