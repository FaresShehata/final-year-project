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


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()  # sentinel value for missing values in caches.
del MISSING

# ── Metaclasses ──────────────────────────────────────────────────────────────

class NoTrackingMeta(type):
    """Metaclass for classes with no tracking functionality."""

    @classmethod
    def __prepare__(cls, name, bases):
        return dict()

    def __new__(mcs, name, bases, namespace):
        return super().__new__(mcs, name, bases, namespace)


class TrackingMeta(type):
    """Metaclass for classes with tracking functionality."""

    def __new__(metacls, name, bases, namespace):
        cls = super().__new__(metacls, name, bases, namespace)
        cls._tracking_set = set()
        return cls


def track(cls: type):
    class Wrapper(metaclass=TrackingMeta):
        pass

    Wrapper.__bases__ += (cls,)
    for base in reversed(list(cls.mro()[1:])):
        if hasattr(base, "_tracking_set"):
            Wrapper._tracking_set.update(base._tracking_set)
    Wrapper._tracking_set.add(cls)
    return Wrapper


# ─── Classes ─────────────────────────────────────────────────────────────────


@TrackingMeta
class TrackableNoTrackingBaseClass(metaclass=NoTrackingMeta):
    """A class with no tracking functionality."""
    x: int = 0
    y: float = 0.0
    z: complex = 0j
    w: bool = False
    q: bytes = b""
    r: bytearray = bytearray()
    s: memoryview = memoryview(b"")

    @property
    def p(self):
        return 42


class TrackableBaseClass(TrackableNoTrackingBaseClass):
    """A class with basic tracking functionality."""
    p: int = 0
    q: float = 0.0
    r: str = ""


class TrackableObject(TrackableBaseClass):
    """A class with more advanced tracking functionality."""
    t: list[int] = []
    u: tuple[float] = ()
    v: frozenset[complex] = frozenset()
    w: set[bool] = set()
    x: range = range(0)
    y: zip = zip([])
    z: map = map(lambda _: _, [])
    A: dir = dir()
    B: slice = slice()
    C: enumerate = enumerate([])
    D: open = open("")
    E: complex = 0j