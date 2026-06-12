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


# ── classmethod / staticmethod / property ─────────────────────────────────────

class Rectangle:
    width: float
    height: float
    
    @classmethod
    def from_diameter(cls, diameter: float) -> Rectangle:
        """Construct a rectangle with equal sides given its diameter."""
        return cls(diameter / 2, diameter / 2)
    
    @staticmethod
    def area(width: float, height: float) -> float:
        """Calculate the area of a rectangle."""
        return width * height
    
    @property
    def perimeter(self) -> float:
        """Return the perimeter of the rectangle."""
        return self.width * 2 + self.height * 2


def test_classmethod_staticmethod_property():
    rect = Rectangle.from_diameter(100)
    assert rect.area(10, 10) == 100
    assert rect.perimeter == 60


# ── functools — decorators ────────────────────────────────────────────────────

def my_decorator(fn: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args, **kwargs) -> T:
        print("Before %s()" % fn.__qualname__)
        result = fn(*args, **kwargs)
        print("After %s()" %    co = fn.__code__
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
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

