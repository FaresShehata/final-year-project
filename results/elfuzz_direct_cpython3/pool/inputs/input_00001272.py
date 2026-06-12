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
    label: str = ""

    def length(self) -> int:
        return self.end - self.start


# ── Context manager helpers ────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions, **kwargs):
    try:
        yield
    except exceptions as e: pass
    if kwargs.pop('preserve_context', False):
        try: reraise(*sys.exc_info())  # type: ignore[attr-defined]
        finally: del sys.exc_info()


<|file_sep|>/seed-07.py
#!/usr/bin/env python3
#
# Seed 18 — Asyncio, multiprocessing, subprocess, selectors, sockets,
#           file descriptors, pipes, select, signals
#

import abc
import asyncio
import collections.abc
import contextvars
import enum
import errno
import functools
import io
import itertools
import logging
import operator
import os
import platform
import re
import signal
import socket
import ssl
import subprocess
import sys
import time
import types
import typing as ty
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass, field
from datetime import date, datetime, timezone, timedelta
from functools import partial
from inspect import signature
from pathlib import Path
from pprint import pformat
from random import randrange
from statistics import mean
from threading import local
from timeit import Timer
from types import TracebackType
from typing import (
    Any,
    TYPE_CHECKING,
    Awaitable,
    BinaryIO,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

if TYPE_CHECKING:
    from collections.abc import KeysView, ValuesView, ItemsView
else:
    from typing_extensions import KeysView, ValuesView, ItemsView


# ── Utilities ────────────────────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    """Primality test using 6k+-1 optimization."""
    if n <= 3:
        return n > 1
    elif not n % 2 or not n % 3:
        return False
    i = 5
    while i * i <= n:
        if not n % i or not n % (i + 2):
            return False
        i += 6
    return True


def primes(_max: int=1_000_000) -> Iterator[int]:
    """Generate an infinite sequence of prime numbers.

    >>> print(list(itertools.islice(primes(), 10)))
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    yield from (n for n in range(2, _max+1) if is_prime(n))


def fibloop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()


# ── Decorators ─────────────────────────────────
class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
