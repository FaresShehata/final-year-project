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
        else:
            return getattr(obj, self.name)

    def __set__(self, obj, value: T):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"value must be {self.expected_type}")
        elif self.lo is not None and value < self.lo:
            raise ValueError(
                f"value must be greater than or equal to {self.lo}"
            )
        elif self.hi is not None and value > self.hi:
            raise ValueError(
                f"value must be less than or equal to {self.hi}"
            )

        setattr(obj, self.name, value)


@functools.total_ordering
class Point:
    x = TypedDescriptor(int)
    y = TypedDescriptor(int)

    def __eq__(self, other):
        return (
            isinstance(other, Point),
            self.x == other.x,
            self.y == other.y,
        )[-1]

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)


# ── Metaclass ────────────────────────────────────────────────────────────────


class SingletonType(type):
    """
    A metaclass for creating singletons.

    Provides the `singleton` decorator.
    """

    _instances: dict[type, object] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> object:
        # If the class has already been instantiated...
        if cls in cls._instances:
            # ...return the existing instance.
            return cls._instances[cls]
        else:
            new_instance = super().__call__(*args, **kwargs)

            # Store it in our little cache.
            cls._instances[cls] = new_instance

            return new_instance

    @staticmethod
    def singleton(cls):
        """A decorator for making classes singletons."""
        old_new = cls.__new__

        @functools.wraps(old_new)
        def new_new(*args, **kwds):
            if cls not in SingletonType._instances:
                SingletonType._instances[cls] = old_new(cls, *args, **kwds)
            return SingletonType._instances[cls]

        cls.__new__ = new_new
        return cls


# ── Context Managers ──────────────────────────────────────────────────────────


@contextlib.contextmanager
def suppress_exception(exception_types=Exception):
    try:
        yield
    except
    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
