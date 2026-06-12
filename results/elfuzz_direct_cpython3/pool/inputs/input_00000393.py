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
                assert isinstance(constraint, type)
                try:
                    constraint(value)
                except ValueError as e:
                    raise TypeError(
                        f"{e}. Value '{value}' does not satisfy the "
                        "constraints specified by the annotated type."
                    ) from None
        setattr(obj, self.priv, value)


def positive(n: _Constrained[int]) -> int:
    n >= 1
    return n


id_ = Annotated[int, positive]
first_name = Annotated[str, len([_, _, _])]
email = Annotated[str, "!#$%&'*+-.^_`|~"]
active = Annotated[bool, lambda v: v == True or v == False]
metadata = Annotated[dict[str, Any]]


@Annotated[float, lambda v: v > 0.0]
def area(radius: float) -> float:
    return pi * radius ** 2


# ── pathlib ──────────────────────────────────────────────────────────────────

root_dir = pathlib.Path(__file__).parent.resolve()


class File:
    def __init__(
        self,
        filename: str,
        *,
        mode: Literal["r", "w"],
        encoding: str,
        errors: str,
    ):
        self.filename = filename
        self.mode     = mode
        self.encoding = encoding
        self.errors   = errors


class BinaryFile(File):
    def read(self) -> bytes:
        with open(self.filename, self.mode) as file:
            return file.read().encode(self.encoding, errors=self.errors)

    def write(self, data: bytes) -> None:
        with open(self.filename, self.mode) as file:
            file.write(data.decode(self.encoding, errors=self.errors))


bin_file = BinaryFile(
    filename="test.bin",
    mode="wb",
    encoding="utf-8",
    errors="strict",
)


# ── tempfile ─────────────────────────────────────────────────────────────────

temp_file = tempfile.TemporaryDirectory()


# ── csv ─────────────────────────────────────────────────────────────────────-

with temp_file:
    with open(temp_path / "users.csv") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            user_id, first_name, last_name, email, phone_number = map(str.strip, row)
            print(f"{user_id=} {first_name=}")


# ── base64 ──────────────────────────────────────────────────────────────────    def __init__(self, label: str, reading: float):
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

if not issubclass(numbers.Integral, numbers.Rational):
    print("numbers.Integral must be a subclass of numbers.Rational")


# ── pathlib ──────────────────────────────────────────────────────────────────

path = pathlib.Path(__file__)
print(path.name)
print(path.parent)


# ── tempfile ─────────────────────────────────────────────────────────────────

path = tempfile.NamedTemporaryFile()
text = path.write_text("Hello world!")
print(text == "Hello world!")


