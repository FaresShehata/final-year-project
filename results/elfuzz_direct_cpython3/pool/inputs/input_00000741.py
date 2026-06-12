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
    "Emax":      999999.0,
    "Emin":      -999999.0,
    "Etiny":     7e-39,
    "eps":       2.220446049250313e-16,
    "machep":    52,
    "max":       1.7976931348623157e+308,
    "min":       2.2250738585072014e-308,
    "smallest": 2.2250738585072014e-308,
}


class FloatInfo(numbers.FloatInfo):

    #   default_float_info values are used by default

    __slots__ = ()

    def __new__(cls, **kwds):
        m = super().__new__(cls)
        m._update(**kwds)
        return m

    @property
    def eps(self):
        return self.eps * 2

    @eps.setter
    def eps(self, v):
        self._update(Eps=v)

    @property
    def tiny(self):
        return self.tiny / 2

    @tiny.setter
    def tiny(self, v):
        self._update(Machep=-round(math.log(v/self.min)) + 1)

    def _update(self, **kwargs):
        max_ = kwargs.pop("Max", None) or self.max
        min_ = kwargs.pop("Min", None) or self.min
        super()._update(Max=max_, Min=min_)

        if kwargs:
            raise TypeError(
                f"FloatInfo.update() got unexpected keyword arguments "
                "{', '.join(kwargs.keys())}"
            )


# ── PathLib ─────────────────────────────────────────────────────────────────

class Path(pathlib.Path):  # pragma: no cover
    """
    Subclass of :py:class:`pathlib.Path` providing additional utilities.

    .. note:: This class is not available under ``pypy``.
    """

    def touch(self, mode=0o666, exist_ok=True):
        """Like :func:`os.utime`, but also creates the file if it does not
        exist."""
        with suppress(File