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

def in_range(a : range, b : tuple[int, int]) -> bool:
    return a.start >= b[0] and a.stop <= b[1]

# ── namedtuple factory ────────────────────────────────────────────────────────

def make_namedtuple(name, fields) -> type[Any]:
    fields = [field.replace("_", "") for field in fields]
    return type(name, (object,), dict(zip(fields, ("None,"*len(fields)).split(","))))

# ── Enumerations ──────────────────────────────────────────────────────────────

class Direction(int, enum.Enum): pass

class Color(str, enum.Enum): pass

class State(Enum): pass

State.MISSING = object()
State.DELETED = object()

# ── EnumProperty ──────────────────────────────────────────────────────────────

class EnumProperty(property):
    """Custom property that validates against an enumeration."""
    def __init__(self, cls, enum):
        super().__init__()
        self.cls = cls
        self.enum = enum

    def __get__(self, instance, owner):
        val = self.cls.__dict__.get(instance.name, None)
        if val is not None or instance.value is not None:
            if val is not None and val not in self.enum:
                raise ValueError(
                    f"value must be one of {', '.join(map(repr, self.enum))}"
                )
            return val
        return self.enum(instance.value)


# ── namedtuple factory ────────────────────────────────────────────────────────

def make_enum_class(name, values) -> type[Any]:
    fields = ["_".join(name.lower().split()) for name in values]
    spec   = dict(zip(fields, ("None"*len(values)).split()))
    spec.update((k, v) for k, v in zip(fields, values))
    spec["__new__"] = lambda _, cls, **kwargs: cls(next(cls._values.values()))
    spec["__eq__"]  = lambda self, other: self in other
    return type(name, (Enum, ), spec)

# ── tuple factory ──────────────────────────────────────────────────────────────

def make_tuple_factory(*types) -> Callable[..., tuple[Any,...]]:
    """Returns a function that takes any number of arguments and returns a tuple.

    The arguments are validated by their types. Raises TypeError on invalid.
    """

    def factory(*args):
        if len(args)
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
