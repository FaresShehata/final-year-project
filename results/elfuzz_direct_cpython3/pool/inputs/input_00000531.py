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
    return x > 0


def negative(x) -> bool:
    return x < 0


def even(x) -> bool:
    return x % 2 == 0


def odd(x) -> bool:
    return x % 2 != 0


IntConstraint: TypeAlias = Annotated[int, Callable[[int], bool]]


# ── Annotated constraints (compile-time-checked via type checkers) ───────────

Annotation: TypeAlias = ("None" | "bool" | "str" | "float" | "int" | "list") | tuple["Annotation", ...]
"""Holds the annotation of a typed variable."""


def _check_annotation(t, v):
    """Check that t is compatible with v."""
    if isinstance(v, tuple):
        # Check all elements separately.
        for i, e in enumerate(v):
            _check_annotation(t[i], e)
    else:
        try:
            if isinstance(t, tuple):
                # Convert to a single type.
                t = t[0]
            if t == "None":
                assert v is None
            elif t == "bool":
                assert isinstance(v, bool)
            elif t == "str":
                assert isinstance(v, str)
            elif t == "int":
                assert isinstance(v, int)
            elif t == "float":
                assert isinstance(v, float)
            elif t == "list":
                assert isinstance(v, list)
        except AssertionError:
            print(f"Failed at {t}, {v}")
            raise TypeError()


def _is_simple_annotation(annotation: Annotation) -> bool:
    """Return True iff `annotation` is a simple type annotation."""
    return isinstance(annotation, str) and annotation not in {"tuple", "Annotated"}


def _resolve_annotations(t, v):
    """Resolve the annotation by replacing it with its actual argument."""
    if isinstance(t, tuple):
        # Replace each element individually.
        return tuple(_resolve_annotations(t[i], v[i]) for i in range(len(t)))
    elif _is_simple_annotation(t):
        # Return the annotation itself.
        return t
    else:
        # Get the actual value from the dictionary.
        return v[t]


def _annotated_signature(func):
    """Get the annotated signature of func."""
    # A class method can be defined without parameters, but has no arguments.
    argspec = inspect.signature(func).replace(parameters=[*inspect.signature(func