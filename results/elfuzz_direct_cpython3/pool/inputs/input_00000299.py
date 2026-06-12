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
        assert isinstance(value, self.expected), \
               f"{obj!r}.annotated_value must be {self.expected}"
        setattr(obj, self.priv, value)


class NonEmpty(str): pass
class Positive(int): pass
class ZeroOrMore(int): pass
class Integer(Annotated[int, NonEmpty]):
    expected = NonEmpty
NonEmptyInteger = Integer
PositiveInt = Integer[Positive]
ZeroOrMoreInt = Integer[ZeroOrMore]

# ── Annotated with type aliases (for type hinting only) ──────────────────────

@typing.overload
def annotated(typ: TypeAlias, *args, **kwargs):
    ...

@typing.overload
def annotated(
    typ: TypeAlias, 
    *,
    validator: Predicate,
):
    ...

@typing.overload
def annotated(
    typ: TypeAlias, 
    *, 
    validator: Predicate,
    message: str,
):
    ...

def annotated(*args, **kwargs):
    return Annotated[
        *[a for a in args],
        *[v for v in kwargs.values()],
    ]



# ── Annotated with class attributes (for type hinting only) ──────────────────

ANNOTATED_VALUE  : ClassVar[_Constrained] = _Constrained()
ANNOTATED_MESSAGE: ClassVar[_Constrained] = _Constrained()


# ── Function parameters ──────────────────────────────────────────────────────

def parameterize(**params):
    """Decorator that annotates function parameters."""
    def deco(func):
        sig = inspect.signature(func)
        for param in params.keys():
            assert param not in sig.parameters, \
                   f"'{param}' appears twice in '{func.__qualname__}'"
        new_params = {k:v[1:] for k,v in params.items()}
        new_sig    = sig.replace(parameters=[*sig.parameters.values(), *new_params.values()])
        func.__signature__ = new_sig
        return func
    return deco


# ── Class methods ────────────────────────────────────────────────────────────

class BaseClass:
    @classmethod
    def cls_method(cls):
        print(f"called from {cls!r}")

BaseClass.cls_method()


# ── Properties ──────────────────────────────────────────────────────────────

class MyClass:
    @property
    def prop(self):
        return 