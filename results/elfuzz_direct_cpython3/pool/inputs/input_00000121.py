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
    tag:   str


# ── class variables vs. instance properties (static/class methods) ────────────

class BaseResource(object):

    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_path(cls, path: pathlib.Path) -> BaseResource:

        # get size of file at `path` on disk; this will fail if the resource
        # doesn't exist or isn't readable.
        with open(path, "rb") as fd:
            size = fd.seek(0, os.SEEK_END)

        return cls(path, size)


    def __init__(self, path: pathlib.Path, size: int):
        self.path   = path
        self.size   = size
        self.active = True


    def close(self):
        pass



# ── parameters are passed by position (or keyword) ────────────────────────────

def factorial(n: int, *, verbose: bool = False) -> int:
    """Return the factorial of a non-negative integer.

    :param n: The number whose factorial should be computed.
    :param verbose: Whether to print progress messages while computing the
        result.

    """
    assert n >= 0, f"n must be non-negative but was {n}"
    if verbose:
        print("Computing", n)

    result = 1
    for i in range(2, n + 1):
        result *= i
        if verbose:
            print(i, "factorial =", result)
    return result


# ── TypedDict combined with a static property ─────────────────────────────────

class ItemCount(TypedDict):
    count: int
    item:  str


class ReportItem:
    items: List[ItemCount]

    def __init__(self, *items: ItemCount):
        self.items = list(items)



# ────────────────────────────────────────────────────────────────────────────
# ───────────────────────────────────── Public API ────────────────────────────
# ────────────────────────────────────────────────────────────────────────────

def main():
    # 1. concurrency: threadpool executor (multiprocessing.pool.Pool also fine)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = [pool.submit(factorial, x, verbose=True) for x in range(3)]
        for future in as_completed(results):
           