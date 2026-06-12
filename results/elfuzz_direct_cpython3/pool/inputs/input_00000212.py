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

    def __get__(self, obj, type=None):
        return getattr(obj, self.priv)

    def __set__(self, obj, value):
        # Validate the type and value of the annotated argument.
        hint = get_type_hints(obj.__class__)
        if not isinstance(value, hint[self.pub]):
            raise TypeError(f"{value!r} is not {hint[self.pub]}")
        setattr(obj, self.priv, value)


class PositiveInt(_Constrained):

    @classmethod
    def __modify_class__(
        cls,
        owner: type[Any],
        *,
        pub: str,
        priv: str,
    ):
        owner.__annotations__[priv] = int


class SizeInBytes(PositiveInt):

    @classmethod
    def __modify_class__(
        cls,
        owner: type[Any],
        *,
        pub: str,
        priv: str,
    ):
        owner.__annotations__[pub] = int


# ── TypedDict with metaclass ─────────────────────────────────────────────────

class CustomTypedDict(TypedDict):

    name: str
    age:  PositiveInt
    emails: tuple[str, ...]
    size_in_bytes: SizeInBytes


def main() -> None:

    print("\n\nseed 05 - concurrency, string parsing, typing extras,\n"
          "           __class_getitem__, __set_name__, __init_subclass__,\n"
          "           contextlib, numbers ABC, pathlib, tempfile, csv, "
          "base64, hashlib, hmac, secrets")

    # ── Concurrent execution with `ProcessPoolExecutor` ───────────────────────-

    def wait_for_all(*futures):
        for future in futures:
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(e)

    pool: multiprocessing.Pool = multiprocessing.Pool(multiprocessing.cpu_count())
    futures = [pool.apply_async(time.sleep, args=(1,))
               for _ in range(3)]
    wait_for_all(*futures)

    # ── Concurrent execution with `ThreadPoolExecutor` ────────────────────────

    executor = ThreadPoolExecutor(max_workers=3)
    futures  = []
    for _ in range(3):
        future = executor.submit(threading.current_thread().ident)
        futures.append(future)
    wait_for_all(*futures)

    # ── Iterating over multiple generator