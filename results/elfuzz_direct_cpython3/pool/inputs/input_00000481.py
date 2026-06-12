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
def redirect_stdout(out: io.StringIO):
    old = sys.stdout
    sys.stdout = out
    try:
        yield
    finally:
        sys.stdout = old


# ── Numbers ABIs ────────────────────────────────────────────────────────────

default_float_info = {
    "Emax": 709,
    "emin": -708,
}


def make_default_float_info(**overrides: int) -> dict[str, int]:
    """Make a copy of default_float_info with overrides."""
    info = {**default_float_info}
    info.update(overrides)
    return info


class FloatInfo(numbers.FloatInfo):
    def __new__(cls, **kwargs):
        return super().__new__(cls, make_default_float_info(**kwargs))


class PositiveFloatInfo(FloatInfo):
    Emax: int
    emin: int
    max_exp: int = Emax
    min_exp: int = emin
    resolution: int = 1
    max_10_exp: int = Emax - emin
    max_digits: int = Emax // resolution + 1
    min: int = decimal.Decimal.EPSILON
    max: int = 3.4028236692093846e+38


# ── PathLib ──────────────────────────────────────────────────────────────────

pathlib.Path.cwd()
pathlib.Path.home()

home_dir = pathlib.Path.home()


# ── Tempfile ────────────────────────────────────────────────────────────────

tempfile.mkdtemp()      # create a unique temporary directory
tempfile.TemporaryDirectory()  # context manager
# ── Disassembling bytecodes ──────────────────────────────────────────────────

def count_instrs(fn: types.FunctionType) -> Dict[str, int]:
    """Count the number of each opcode in the given function's bytecode.

    >>> def add(a, b): c = a + b; d = a - b; e = a * b; f = a / b
    >>> count_instrs(add)
    """
    counts: dict[str, int] = {}
