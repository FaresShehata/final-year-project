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
CsvRow  : TypeAlias = tuple[Any, ...]


# ── Context manager utilities ────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


@contextlib.contextmanager
def redirect_stdout(fileobj=None, *, close=True):
    old = sys.stdout
    if fileobj is None:
        fileobj = StringIO()
    sys.stdout = fileobj
    try:
        yield fileobj
    finally:
        sys.stdout = old
        if close:
            fileobj.close()


# ── Inheritance chain ────────────────────────────────────────────────────────

class BaseClass:
    def foo(self):
        print(f"foo from {self.__class__.__name__}")


class DerivedClass(BaseClass):
    def bar(self):
        print(f"bar from {self.__class__.__name__}")
        super().bar()

    def baz(self):
        print(f"baz from {self.__class__.__name__} ({self.foo})")


def test_inheritance_chain():
    obj = DerivedClass()
    obj.bar()
    obj.baz()

# ── Traits and protocols ──────────────────────────────────────────────────────

class TraitExample:
    def trait_method(self):
        ...


class ProtocolExample(metaclass=ABCMeta):
    @abstractmethod
    def protocol_method(self):
        ...


# ── Traits and protocols example usage ────────────────────────────────────────

# class Foo(TraitExample, ProtocolExample):
#     ...


# ── Numbers abstract base classes ─────────────────────────────────────────────

class MyInt(int, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> MyInt:
        ...


class MyFloat(float, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> MyFloat:
        ...


# ── Path manipulation ─────────────────────────────────────────────────────────

pathlib.Path.cwd()           # Current working directory
os.path.exists(path_str)      # Whether path exists on filesystem
os.path.join(path_str_a, ...)   # Join parts into one path
pathlib.Path.home()           # Home dir
pathlib.Path.resolve(path_obj)   # Resolve to absolute path
pathlib.Path.is_absolute(path_obj)  # Is it an absolute path?
pathlib.Path.glob(pattern)       # Match files pattern
pathlib.Path.iterdir()        # Iterate over contents of a directory
pathlib.Path.mkdir(mode=..., exist_ok=False)  # Make directory
pathlib.Path.rmdir()             # Remove empty directory
pathlib.Path.rmtree()                # Remove recursively
pathlib.Path.rename(old_name, new_name)   # Rename path
pathlib.Path.unlink()                # Remove path
pathlib.Path.write_text(text, encoding="utf-8")  # Write text to path


# ── Temporal management ───────────────────────────────────────────────────────

tempfile.NamedTemporaryFile(prefix="", suffix="", mode="wb", buffer_size=-1, encoding=None, errors=None, newline=None, delete=True, dir=None)  # noqa  # pyright: ignore
with tempfile.TemporaryDirectory() as tempdirname:
    ...
with tempfile.SpooledTemporaryFile(max_size=...):
    ...


# ── Text processing ───────────────────────────────────────────────────────────

textwrap.shorten(text, width, placeholder="...")
textwrap.fill(text, width, expand_tabs=True,
from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    """Inspect the calling frame.

    Returns dictionary with keys 'caller', 'called' and 'callers_caller'.
    """
    callers_frame = sys._getframe(depth)
    called_frame = callers_frame.f_back
    caller_frame = called_frame.f_back
    return {
        "caller": caller_frame.f_code.co_name,
        "called": called_frame.f_code.co_name,
        "callers_caller": callers_frame.f_back.f_code.co_name,
    }


def get_arg_spec(fn: Callable[..., Any]) -> inspect.FullArgSpec:
    return inspect.getfullargspec(fn)


# ── Garbage collection ────────────────────────────────────────────────────────

def mark_all_garbage() -> None:
    gc.collect()


def collect_all_references() -> Set[Any]:
    refs: set = set()
    gc.get_referrers(refs)
    return refs


# ── Memory allocation statistics ───────────────────────────────────────────────

def memory_usage() -> tuple[int, int]:
    return resource.getrusage(resource.RUSAGE_SELF)[2], resource.getrusage(resource.RUSAGE_SELF)[4]


# ── Type hinting ──────────────────────────────────────────────────────────────

def my_sum(numbers: Iterable[float]) -> float:
    sum_ = 0.0
    for number in numbers:
        sum_ += number
    return sum_


def my_sum_generic(numbers: Sequence[float]) -> float:
    sum_ = 0.0
    for number in numbers:
        sum_ += number
    return sum_


# ── Pickling and unpickling ───────────────────────────────────────────────────

class ColoredPoint(Point):
    color: str


def pick_state(point: Point) -> bytes:
    return pickle.dumps({"x": point.x, "y": point.y})


def unpick_point(packed_data: bytes) -> Point:
