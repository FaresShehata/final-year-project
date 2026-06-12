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
    label: str
    duration: float
    is_error: bool

    @property
    def elapsed(self):
        return self.end - self.start

# ── Class/instance attributes are named after the class ───────────────────────

class Foo:
    bar: int

foo = Foo()
assert foo.bar == 0

# ── Class variables are stored at the module level ────────────────────────────

Foo.baz = 1
foos = [Foo(), Foo()]

for foo in foos:
    assert foo.baz == 1

# ── Metaclasses can be used to inject instance methods ────────────────────────

class BarMeta(type):

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)
        inst.name = kwargs.pop('name', 'anonymous')
        return inst

class Bar(metaclass=BarMeta):
    pass

bar = Bar(name='some-name')

assert bar.name == 'some-name'

# ── Metaclasses can also alter the metaclass of a subclass ────────────────────

class BazMeta(type):
    def __new__(cls, classname, bases, attrs):
        new_class_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name.startswith('_'):
                new_class_attrs[attr_name] = attr_value
            else:
                new_class_attrs[f'is_{attr_name}_baz'] = lambda self: attr_name == 'baz'
        return super().__new__(cls, classname, bases, new_class_attrs)

class Baz(metaclass=BazMeta):
    baz: int

b = Baz(baz=3)

assert b.is_baz()

# ── The _abc_registry attribute contains all registered classes and metaclasses ─

print(Foo.__subclasses__())
print(Bar._abc_registry)