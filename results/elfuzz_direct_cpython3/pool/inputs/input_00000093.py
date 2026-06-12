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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()
    
    @classmethod
    def get_all_shapes(cls) -> list[type[Shape]]:
        return [*cls._registry.values()]


class Rectangle(Shape):
    width: int = TypedDescriptor(int, 0, 500)
    height: int = TypedDescriptor(int, 0, 500)

    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __str__(self) -> str:
        return (
            f"{self.label}\n"
            f"\twidth: {self.width}\n"
            f"\theight: {self.height}\n"
            f"\tarea: {self.area():.4f}\n"
            f"\tperimeter: {self.perimeter():.4f}"
        )

    def scale_size(self, factor: int | float) -> None:
        self.width *= factor
        self.height *= factor


class Square(Rectangle):

    side_length: int = TypedDescriptor(int, 0, 1_000)

    def __init__(
        self,
        side_length: int = 100,
        *,
        color: str = "blue",
        shape: Optional[Type[Rectangle]] = None,
    ) -> None:
        self.side_length = side_length
        super().__init__(shape=color or self.shape_color(), color=color)

    def shape_color(self) -> str:
        return self.color.lower()


# ── Decorators ────────────────────────────────────────────────────────────────

class ProfiledDecorator(object):
    """
    Decorator that profiles a function on execution.

    Profiling data are stored in the `profile` attribute.
    """

    def __init__(self, func):
        self.func = func
        self.profile = []

    def __call__(self, *args, **kwargs):
        profile = {}
        time_start = perf_counter_ns()
        result = self.func(*args, **kwargs)
        time_end = perf_counter_ns()

        elapsed_time = time_end - time_start
        profile["elapsed"] = elapsed_time / 1_000_000
        profile["calls"] = 1
        profile["avg-cpu-time"] = elapsed_time / args[0]
        profile["max-cpu-time"] = max(args[0], kwargs