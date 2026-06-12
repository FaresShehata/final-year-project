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

    def __repr__(self) -> str:
        n, u = divmod(self.reading, 1)
        m, s = divmod(n, 60)
        h, t = divmod(m, 60)
        return f'{h} hours {t:.3f}s'

# ── ParamSpec ────────────────────────────────────────────────────────────────

def concat[T](x: T, y: T) -> tuple[T, ...]: return x, y

A = ParamSpec("A")
B = ParamSpec("B")


# ── TypeVar ─────────────────────────────────────────────────────────────────

Tm = TypeVar("Tm", bound=numbers.Integral)
Ts = TypeVar("Ts", int, float)

# ── ClassVar ────────────────────────────────────────────────────────────────

class Foo:
    data: ClassVar[list[int]] = []

    def add_data(self, d: int):
        self.data.append(d)

foo = Foo()
foo.add_data(1)
assert foo.data == [1]
foo.data = [99]
assert foo.data == [99]

bar = Bar()
assert bar.data == [1]
bar.data = [99]
assert bar.data == [99]



# ── TextWrapper ─────────────────────────────────────────────────────────────-

for line in textwrap.wrap('Hello my friend', width=10, expand_tabs=False):
    print(repr(line))

# ── StringIO ─────────────────────────────────────────────────────────────────

print(io.StringIO())
io.StringIO().write("hello world\n")

# ── BufferedRandom ──────────────────────────────────────────────────────────

with open(__file__) as f:
    buf = io.BufferedReader(f).readline()

# ── BytesIO ─────────────────────────────────────────────────────────────────

buf = io.BytesIO(b"\xff\xff\xff\xff\x00\x00\x00\x00".replace(b"\xFF", b"\xFE"))
buf.getvalue()


# ── CSV ─────────────────────────────────────────────────────────────────────

csv.writer(io.StringIO()).writerow(["a", "b"])
csv.reader(io.StringIO("a,b")).next()

# ── Path-like objects ───────────────────────────────────────────────────────

path = pathlib.Path("/tmp/test.txt").open("wb").close()
path = pathlib.Path("/tmp/test.txt")
path.is_file(), path.exists(), path.stat(), path.unlink()

path = "/tmp/test.txt"
path = pathlib.Path(path)
path.is_file(), path.exists(), path.stat(), path.unlink()

os.chdir("/")
path = "/test/"
path = pathlib.Path(path)
path.is_dir(), path.existsfrom sys import argv, version_info
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
