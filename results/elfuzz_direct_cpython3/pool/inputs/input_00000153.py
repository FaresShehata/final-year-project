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

    @property
    def average(self) -> float:
        return sum(self.reading / len(self._readings))

    @property
    def max_reading(self) -> float:
        return max(self._readings)

    @classmethod
    def from_json(cls, json: JsonValue) -> Sensor:
        try:
            return cls(json["label"], json["reading"])
        except KeyError as exc:
            raise ValueError("invalid sensor") from exc


# ── ParamSpec ────────────────────────────────────────────────────────────────

def divide_chunk(n, chunk_size=32):
    """Divide n into chunks of size at most chunk_size."""
    assert isinstance(chunk_size, int) and chunk_size >= 1
    for i in range(0, n, chunk_size):
        yield slice(i, min(i + chunk_size, n))


def probe(
    tasks: Sequence[Sensor],
    chunk_size: int = 32,
    min_delay: float = 0.01,
    max_delay: float = 0.1,
    **kwargs
) -> None:

    delay = random.uniform(min_delay, max_delay)

    for task in tasks:
        print(f"Starting {task}")

        with task.to_file("json", encoding="utf-8") as fileobj:
            fileobj.write(task.json())

        time.sleep(delay)


# ── Context managers ──────────────────────────────────────────────────────────

class Suppress(contextlib.AbstractContextManager):
    """Suppress exceptions inside a block.

    >>> with Suppress(ValueError):
    ...    raise Exception()
    """

    def __enter__(self): pass
    def __exit__(self, *exc_info):
        return True


@contextlib.contextmanager
def redirect_stdout(new_target):
    old_target = sys.stdout
    new_target = io.TextIOWrapper(io.BytesIO())
    sys.stdout = new_target
    try:
        yield new_target
    finally:
        sys.stdout.detach()
        sys.stdout = old_target


with open("/tmp/somefile.txt") as fh:
    line = next(fh)
print(line)

with redirect_stdout(sys.stderr.buffer) as stderr:
    print("something went wrong!", file=sys.stderr)

line = next(stderr)
stderr.write(b"other stuff\n")

# ── Numbers abstract base class ───────────────────────────────────────────────

class MyInt(int):

    def __add__(self, other):
        if other % 2            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

