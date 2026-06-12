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
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)

    def __delete__(self, obj):
        delattr(obj, self.name)


class Integer(TypedDescriptor):
    """Integer descriptor."""


class Float(TypedDescriptor):
    """Float descriptor."""


class String(TypedDescriptor):
    """String descriptor."""


class RangeRange(object):
    """Custom range class."""

    def __init__(self, start, stop=None, step=1):
        if step == 0:
            raise ValueError("step cannot be 0.")
        if isinstance(start, float):
            start, stop, step = map(float, (start, stop, step))
        elif isinstance(stop, float):
            start, stop, step = map(int, (start, stop, step))

        self.start = start
        self.stop = stop
        self.step = step

    def __eq__(self, other):
        return (
            isinstance(other, RangeRange)
            and self.start == other.start
            and self.stop == other.stop
        )

    def __contains__(self, item):
        if self.step != 1:
            return False
        if self.start >= self.stop:
            return self.start == item and self.stop == item
        else:
            return self.start <= item < self.stop

    def __repr__(self):
        args = repr(self.start), repr(self.stop), repr(self.step)
        return "{cls}({args})".format(cls=self.__class__.__name__, args=", ".join(args))

    def __iter__(self):
        i = self.start
        while True:
            if i >= self.stop:
                break
            yield i
            i += self.step

    def __len__(self):
        """Return number of items."""
        if self.step == 1:
            return max((self.stop - self.start) // self.step, 0)
        else:
            return len(list(itertools.takewhile(lambda x: x < self.stop, iter(self))))

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            new_range = list(range(len(self))[idx])
            return RangeRange(*(self[i] for i in new_range))
        else:
            i = idx % len(self)
            return self.start + i * self.step


class RangeDescriptor(TypedDescriptor):
    """Range descriptor."""

    def __init__(self, expected_type=range, lo=..., hi=...):
        super().__init__(expected_type, lo, hi)


class _WeakSet(set):
        # Note: We're using a memory cache here (like CPython does for methods).
        # If you need an actual cache that survives between multiple calls,
        # use `functools.lru_cache` instead.
        if instance is None:
            return self
        if self.attrname is None:
            raise AttributeError("Untyped cached property")
        try:
            attr = getattr(instance, self.attrname)
        except AttributeError:
            attr = self.func(instance)
            setattr(instance, self.attrname, attr)
        return attr


# ── Metaclass ────────────────────────────────────────────────────────────────

class Meta(type):
    """Metaclass that adds a static method to all subclasses of Base."""

    @staticmethod
    def new_method():
        ...


# ── Classes and objects ───────────────────────────────────────────────────────

class Base(metaclass=Meta):  # class Foo(abc.ABC, object):
    pass

assert hasattr(Base, "new_method")

# ── Context Managers ─────────────────────────────────────────────────────────-

@contextlib.contextmanager
def open_file(path: str) -> Iterator[None]:
    print("Opening file...")
    yield
    print("Closing file...")


with open_file("/tmp/test") as f:
    ...


# ── Generators ───────────────────────────────────────────────────────────────

@functools.cache
def fib(n: int) -> int:
    assert n >= 0
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


fib_generator = (n for n in range(sys.maxsize))


# ── Pickling ─────────────────────────────────────────────────────────────────

from pickle import Unpickler, dumps, HIGHEST_PROTOCOL

data = {
    "a": [1, 2.0, 3, 4+6j],
    "b": ("string", b"byte"),
    "c": {"d": [9, 8.0, 7, 6+content_packed = pickle