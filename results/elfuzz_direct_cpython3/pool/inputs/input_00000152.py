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
    AsyncIterator,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Deque,
    Dict,
    ForwardRef,
    Generator,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    Match,
    NoReturn,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    ValuesView,
    overload,
)
from collections.abc import CallableMeta, CoroutineMeta, SequenceMeta
from dataclasses import dataclass, field, InitVar, fields, is_dataclass, replace
from datetime import date, datetime, timedelta
from enum import Enum
from fileinput import FileInput
from functools import partial, reduce, wraps
from keyword import iskeyword
from math import ceil, factorial, floor, sqrt
from operator import indexOf
from pprint import PrettyPrinter
from reprlib import Repr
from shlex import split
from signal import Signals
from socket import gethostname
from sys import argv, version_info
from types import TracebackType
from typing import TYPE_CHECKING, Any, AnyStr, ClassVar, cast, final, overload
from typing_extensions import (
    Concatenate,
    ClassVar,
    Self,
    SupportsIndex,
    Unpack,
    TypedDict,
    ParamSpec,
    Protocol,
    TypeGuard,
    TypeVarTuple,
    get_args,
)

# PyTorch/TensorFlow/etc.
import torch

if TYPE_CHECKING:
    from .utils import *
else:
    from utils import *


def _gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

@overload
def gcd(a: int, b: int, /) -> int: ...
@overload
def gcd(*args: Union[int, float]) -> int: ...

def gcd(*args: Union[int, float], /):  # noqa: F811
    return reduce(_gcd, args)


@dataclass(slots=True)
class _Constrained(Generic[Any]):
    pub: str      = ""
    priv: str     = ""
    hint: str     = "Any"
    doc: str      = ""
    default: Any = None

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        yield cls.validate

    @classmethod
    def        ann   = hints.get(self.pub)
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

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
