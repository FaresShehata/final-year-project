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

class NonNegativeInteger(Annotated[int, numbers.Integral, numbers.Number]):
    def __post_init__(self): ...


class PositiveFloat(Annotated[float, numbers.Real, numbers.Number]):
    def __post_init__(self): ...


class FiniteNumber(
    Annotated[
        float,
        numbers.Real,
        numbers.Number,
        Predicate[lambda value : -1e3 < value < 1e3],
    ]
):
    def __post_init__(self): ...
    

# ── Context manager for suppressing output ───────────────────────────────────-

@contextlib.contextmanager
def suppress(*exceptions: Exception) -> Iterator[None]:
    original = sys.stdout
    try:
        sys.stdout = open(os.devnull, "w")
        yield
    finally:
        sys.stdout.close()
        sys.stdout = original


# ── Redirect output to a file ─────────────────────────────────────────────────

@contextlib.contextmanager
def redirect_stdout(out: IO[Any]) -> Iterator[None]:
    old_stdout = sys.stdout
    try:
        sys.stdout = out
        yield
    finally:
        sys.stdout = old_stdout


# ── Custom exception type with named fields ───────────────────────────────────

class CustomError(Exception):
    __slots__: ClassVar[tuple[str]] = ()

    # It's a good practice to have the same number of slots as there are attributes.
    # This allows the compiler to optimize memory usage by avoiding padding between class instances.

    def __init__(
        self,
        message: str,
        *,
        code: int = 0,
        status: int = 200,
        headers: dict[str, str] = {},
    ) -> None:
        super().__init__()
        self.message = message
        self.code = code
        self.status = status
        self.headers = headers
        self._repr_html_ = f"<code>{message}</code>"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomError:
        return cls(**data)


# ── Session state within an application thread ────────────────────────────────

class SessionState(dict):

    _session_id: Final[str] = secrets.token_hex()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self["id"] = self.__class__._session_id

    def update(self, *args: Any, **kwds: Any) -> None:
        raise TypeError(f"{type(self).__name__} objects are immutable")


# ── Simple