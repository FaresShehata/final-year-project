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


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

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
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __le__(self, other: Shape) -> bool:
        return self.area() <= other.area()


class Rectangle(Shape):
    width: int
    height: int

    def __init__(self, width: int, height: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height

    def area(self) -> float:     return self.height * self.width
    def perimeter(self) -> float: return (self.width + self.height) * 2

    @classmethod
    def from_area(cls, area: float, *, width: Optional[int]=None, height: Optional[int]=None):
        if width is None or height is None:
            raise TypeError("Rectangle.from_area requires both width and height")
        return cls(width, height, area=area)

    @classmethod
    def from_perimeter(cls, perimeter: float, *, width: Optional[int]=None, height: Optional[int]=None):
        if width is None or height is None:
            raise TypeError("Rectangle.from_perimeter requires both width and height")
        return cls(width, height, perimeter=perimeter)

    @staticmethod
    def get_aspect_ratio(ratio: float) -> tuple[float, float]:
        """Get the dimensions required to have given ratio."""
        return round(sqrt(ratio)), round(sqrt(1 / ratio))

    @CachedProperty
    def aspect_ratio(self) -> float:
        return self.height / self.width

    @CachedProperty
    def diagonal_length(self) -> float:
        return sqrt(self.area())

    @CachedProperty
    def squareness(self) -> float:
        return abs((sqrt(self.area()) - self.diagonal_length) / sqrt(self.area()))

    def __setattr__(self, key, value):
        if key == "width":
            self.height = value
        elif key == "height":
            self.width = value
        else:
            super().__setattr__(key, value)

    def __eq__(self, other: Shape) -> bool:
        return self.area() == other.area()

    def __add__(self, other: Rectangle) -> Rectangle:
        return Rectangle(
            min(self.width, other.width),
            max(self.height, other.height),
            area=self.area() + other.area(),
        )

    def __mul__(self, other: int) -> Rectangle:
        return Rectangle(
            self.width * other,
            self.height *    def numerator(self) -> int:   return self._n
    @property
