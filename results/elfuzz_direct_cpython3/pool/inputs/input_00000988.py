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

# ── Custom type aliases ──────────────────────────────────────────────────────-

T1                     = TypeVar("T1")
T2                     = TypeVar("T2", bound=numbers.Number)


class MyInt(int):
    pass


class MyFloat(float):
    pass


MyNumber: TypeAlias = "float | int"
"""A generic number."""


# ── Typing Extras ────────────────────────────────────────────────────────────

FormattableString: TypeAlias = "str | Formatter"


class Formatter(textwrap.Formatter):
    argnum: int
    fmtstr: FormattableString


# ── Context managers ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exc_types):
    with contextlib.suppress(*exc_types):
        yield


@contextlib.contextmanager
def redirect_stdout(target):
    # https://stackoverflow.com/a/39878839/137529
    original_target = sys.stdout
    try:
        sys.stdout = target
        yield target
    finally:
        sys.stdout = original_target


# ── Numbers ABC ──────────────────────────────────────────────────────────────

MIN_INT:      Final[int] = -2 ** 31
MAX_UINT:     Final[int] = 2 ** 32 - 1
MIN_FLOAT:    Final[float] = (-1.0 / 0.0) + 1.0
MAX_FLOAT:    Final[float] = ((1.0 / 0.0) - 1.0) * (-1.0)
MIN_DBL_EXP:  Final[int] = -(1 << 1023)
MAX_DBL_EXP:  Final[int] = (1 << 1023) - 1
MIN_DBL_MANT: Final[float] = 2 ** (-1074)
MAX_DBL_MANT: Final[float] = (1 - MIN_DBL_MANT) * MAX_DBL_EXP

# ── pathlib ──────────────────────────────────────────────────────────────────

tmpdir_path: pathlib.Path = pathlib.Path(tempfile.mkdtemp())
assert tmpdir_path.exists()
del tmpdir_path

for path in pathlib.Path("tests").glob("**/*.py"):
    print(path.read_text())

# ── tempfile ─────────────────────────────────────────────────────────────────

with tempfile.TemporaryFile() as fp:
    fp.write(b"Hello World!")
fp.seek(0)
print(fp.read().decode())

with tempfile.NamedTemporaryFile(suffix=".txt") as fp:
    pass
with tempfile.SpooledTemporaryFile(max_size=1e6) as fp:
    pass

# ── csv ──────────────────────────────────────────────────────────────────────

fieldnames = ["id", "name", "email"]
rows       = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}, ]
with open(tmpdir_path.joinpath("users.csv"), mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader