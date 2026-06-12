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
    requests:   int


# ── ClassVars ────────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int; g: int; b: int; a: int = 255


class Settings(Generic[T]):
    default_value: T
    values: tuple[T, ...]
    
    def __init__(self, value: T) -> None:
        self.value = value
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={repr(self.value)}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value



# ── Typing Extras ────────────────────────────────────────────────────────────


def foo(x: Annotated[int, "foo", math.exp]) -> Annotated[float, "bar"]:
    ...


def add(a: Annotated[int, "a"], b: Annotated[int, "b"]) -> Annotated[int, "c"]:
    ...


def bar(t: Annotated[type[int], "t"]) -> Annotated[t, "u"]:
    ...


def baz(u: Annotated[U, "v"]) -> Annotated[V, "w"]:

    v: Annotated[V, "x"]
    w: Annotated[W, "y"]

    ...

    return w


# ── __class_getitem__ ────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)
V = TypeVar("V")


class C(Generic[T_co, V]): pass


C[C["X", "Y"], "Z"]


# ── __set_name__ ─────────────────────────────────────────────────────────────

class A(Generic[T]):
    def __init_subclass__(cls: type[A[T]]) -> None:
        assert cls.__annotations__["value"].__origin__ is list
        assert cls.__annotations__["value"].__args__[0].__origin__ is int
        super().__init_subclass__()
    

class B(A[list[int]]): pass


# ── __init_subclass__ ────────────────────────────────────────────────────────

class Parent:
    def __new__(cls, *args, **kwargs):
        print(f"Parent.__new__() called with args {args}, kwargs {kwargs}")
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        print(f"Parent.__init__() called with args {args}, kwargs {kwargs}")


class Child(Parent):
    def __new__(cls, *args, **kwargs):
        print(f"Child.__new__() called with args {args}, kwargs {kwargs}")
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        print(f"Child.__init__() called with args {args}, kwargs {kwargs}")



# ── Context Manager ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def timer() -> Generator[None, None, None]:
    start_time = time.time()
    yield
    end_time = time.time()

    elapsed_seconds = end_time - start_time
    print(f"Took {elapsed_seconds:.3f}s to run the test suite.")



# ── BaseException ────────────────────────────────────────────────────────────

try:
    raise ValueError("abc")
except Exception as e: # noqa
    print(e)


# ── Numbers ABC ─────────────────────────────────────────────────────────────

isinstance(1.0, numbers.Number)

isinstance(-1.0j, numbers.Real)

isinstance(numbers.pi, numbers.Number)

isinstance(numbers.pi, numbers.Real)

# ── pathlib ──────────────────────────────────────────────────────────────────

pathlib.Path.cwd().exists()
pathlib.Path("/").resolve()


# ── tempfile ─────────────────────────────────────────────────────────────────

tempfile.gettempdir()

with tempfile.TemporaryDirectory() as temp_dir_path_str:
    print(temp_dir_path_str)


with tempfile.NamedTemporaryFile(mode="rb") as ttf:
    print(ttf.name)

# ── CSV ──────────────────────────────────────────────────────────────────────

data = [
    ["Name", "Age"],
    ["Alice", "25"],
    ["Bob", "30"],
    ["Charlie", "35"],
]

with open("test.csv", "w") as f:
    writer = csv.writer(f)
    for row in data:
        writer.writerow(row)

with open("test.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)


# ── Base64 ──────────────────────────────────────────────────────────────────

