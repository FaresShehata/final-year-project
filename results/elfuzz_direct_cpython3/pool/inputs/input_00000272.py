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


# ── Decorators ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions: Exception, reraise: bool = False):
    try:
        yield
    except exceptions as e:
        if reraise:
            raise e from None
        else:
            pass

@contextlib.contextmanager
def redirect_stdout(new_target: TextIO):
    old_target, sys.stdout = sys.stdout, new_target
    try:
        yield old_target
    finally:
        sys.stdout = old_target



# ── Data classes ──────────────────────────────────────────────────────────────

class Point(Generic[T]):
    x: T
    y: T

    @classmethod
    def zero(cls) -> Point[T]:
        return cls(0, 0)

    def add(self, other: Point[T]) -> Point[T]:
        return Point[self.type](self.x + other.x, self.y + other.y)

    def mul(self, factor: T) -> Point[T]:
        return Point[self.type](self.x * factor, self.y * factor)

    def __repr__(self) -> str:
        return f"<Point({self.x}, {self.y})>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Point) \
               and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Rational(NamedTuple):
    num: int
    den: int

    def __repr__(self) -> str:
        return f"<Rational({self.num}/{self.den})>"


class ComplexField(float):
    pass

ComplexField.register(complex)



# ── Type variables ───────────────────────────────────────────────────────────

V      = TypeVar('V')
D      = TypeVar('D', bound=Iterable[V])
E      = TypeVar('E', bound=Callable[[V], V])


# ── Callable types (function types w/ generic args) ──────────────────────────

FooFunc = Callable[..., int]
BarFunc = Callable[[str], int]
BazFunc = Callable[[str, int, complex], float]



# ── Custom metaclass ─────────────────────────────────────────────────────────

class Meta(type):

    def __getitem__(cls, item: tuple[int, int]) -> FooClass:
        xHEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

