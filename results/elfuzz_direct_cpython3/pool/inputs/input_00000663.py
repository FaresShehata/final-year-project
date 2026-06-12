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


# ── Context manager helpers ────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions, **kwargs):
    try:
        yield
    except exceptions as e:
        pass


@contextlib.redirect_stdout(None)
@contextlib.redirect_stderr(None)
@contextlib.contextmanager
def redirect_io(stdout, stderr):
    with StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        yield


@contextlib.AbstractContextManager
class AsyncGenerator(Generic[T]):
    async def __anext__(self): ...

    @classmethod
    async def from_iterable(cls, iterable: Iterable[T]) -> AsyncGenerator[T]:
        ...


# ── Classes ────────────────────────────────────────────────────────────────────

class Person(Generic[P]):
    age: P
    name: str
    has_died: bool

    def __str__(self):
        return f"{self.name}: Age {self.age}"


class Human(Person[int]):
    pass


class Robot(Person):
    def __str__(self):
        return f"{self.name}: Age {self.age}"


class Animal(Generic[P], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def speak(self) -> str: ...
    @property
    @abc.abstractmethod
    def name(self) -> str: ...


class Dog(Animal[int]):
    def speak(self) -> str:
        return "Woof!"
    @property
    def name(self) -> str:
        return "Fido"

# ── Enumerations ───────────────────────────────────────────────────────────────

class Category(Enum):
    BOOKS  = "books"
    MUSIC  = "music"
    MOVIES = "movies"

class BookCategory(Category):
    SCIENCE_FICTION = "science_fiction"


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass(order=True)
class Employee:
    first: str
    last:  str
    pay:   int

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# ── Decorators ─────────────────────────────────────────────────────────────────

def trace(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args, **kwds):
        print(f"Calling {func.__qualname__}")
        result = func(*args, **kwds)
        print(result)
        return result
    return wrapper

@trace
def add(a: int, b:int) -> int:
    return a + b

add(1, 2)


# ── Type hinting ───────────────────────────────────────────────────────────────

x: int           # not checked by mypy or pyright
y: int = 3       # also not checked by them
z: int = 4       # it's an error!
a: bytes         # this should be of the form 'bytes',

