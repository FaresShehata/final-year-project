"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
            raise ValueError(f"{value} out of bounds [{self.lo}, {self.hi}]")
        
        setattr(instance, self.name, value)
        
    def __get__(self, instance: T, owner: type[T] | None = None) -> Any:
        if instance is None:
            return self
        else:
            return getattr(instance, self.name)

class IntegerTyped(TypedDescriptor):
    def __set__(self, instance: T, value: int) -> None:
        super().__set__(instance, value)

class FloatTyped(TypedDescriptor):
    pass

class StringTyped(TypedDescriptor):
    def __set__(self, instance: T, value: str) -> None:
        super().__set__(instance, value.encode()) # TODO: Make sure to decode the value when __get__() is called.


# ── Context manager ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def timer() -> Generator[None, None, None]:
    """A simple context manager that times how long the code inside its block takes."""
    start_time = time.time()
    yield
    print("Time elapsed:", time.time() - start_time)


# ── Generators ───────────────────────────────────────────────────────────────

def my_generator(n: int) -> Iterator[int]:
    for i in range(n):
        yield i*i


# ── Metaclasses ──────────────────────────────────────────────────────────────

class MyMeta(type):

    @classmethod
    def get_nice_name(cls) -> str:
        return f"{cls.__name__}"

    def __new__(mcs, name: str, bases: tuple[type], attrs: dict[str, Any]) -> type:
        nice_name = mcs.get_nice_name()
        attrs["nice_name"] = nice_name
        return super(MyMeta, mcs).__new__(mcs, name, bases, attrs)

    def __str__(cls) -> str:
        return cls.nice_name

    def __repr__(cls) -> str:
        return "<Class %s>" % cls.nice_name


class MyClass(metaclass=MyMeta): 
    pass


# ── Enumerations ─────────────────────────────────────────────────────────────

class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 4
    YELLOW = 8

print(Color.RED.value)


# ── Iterators ────────────────────────────────────────────────────────────────

def run_once(func: Callable[[Any], Any]) -> Callable[[AnyHEADER_SIZE = struct.calcsize(HEADER_FMT)


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

def run_around_view(array_func: types.FunctionType) -> None:
    """Run around an array or memoryview by converting it to/from a byte string.

