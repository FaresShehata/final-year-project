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

# ── ParamSpec ────────────────────────────────────────────────────────────────

def my_func(a: int, b: int = 1, /, c: int = 3, *, d: int = 4, e: int = 5) -> None:
    ...

print(my_func.__annotations__)  # {'a': int, 'b': int, 'c': int, 'd': int, 'e': int}

ArgType = ParamSpec('ArgType')
KwargsType = ParamSpec('KwargsType')

def func(
    *,
    a: ArgType['x'],
    b: KwargsType['y'] = 'hi',
    z: KwargsType['z'] = None,
    **kwargs: KwargsType[Any]
) -> None:
    ...

t = get_type_hints(func, include_extras=True)
assert t["a"] == ArgType  # OK!
assert t["b"].values() == tuple(KwargsType.values())  # OK!

# ── Contextmanager with no arguments ─────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exc_types):
    try:
        yield
    except exc_types:
        pass  # Ignore exceptions.

with open(__file__) as src_file, suppress(ValueError):
    print(src_file.read())

# ── suppress context manager with exception argument ─────────────────────────

try:
    raise ValueError()
except Exception as err:
    with suppress(TypeError):
        raise ValueError()

# ── suppress context manager with exception argument and type hint ───────────

try:
    raise ValueError()
except Exception as err:
    with suppress(ValueError, TypeError):
        raise ValueError()

# ── contextlib.redirect_stdout ───────────────────────────────────────────────

with open("/dev/null", "w") as dev_null:
    with contextlib.redirect_stdout(dev_null):
        print("Hello")

# ── contextlib.redirect_stderr ───────────────────────────────────────────────

with open("/dev/null", "w") as dev_null:
    with contextlib.redirect_stderr(dev_null):
        print("Error:", file=sys.stderr)

# ── contextlib.AbstractContextManager ────────────────────────────────────────

class MyContextManager(contextlib.AbstractContextManager[T]):
    def __enter__(self) -> T:
        ...
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[True]:
        ...
        
# ── Annotated ────────────────────────────────────────────────────────────────

def foo(x=Annotated[int, lambda x: x > 0]):
    pass

foo(1)  # OK.
foo(-2)  # Raises the following error.
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "<stdin>", line 2, in foo
# TypeError: Annotated annotation failed on parameter 'x' of function 'foo'
# Reason was: Annotated annotation failed on parameter '