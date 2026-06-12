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
            raise TypeError(f"Expected {value}, got {type(value)}")
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name} must be greater than or equal to {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name} must be less than or equal to {self.hi}")
        setattr(obj, self.name, value)

class IntTyped(TypedDescriptor):
    """Simple integer descriptor with no constraints."""
    def __set__(self, obj, value) -> None:
        super().__set__(obj, int(value))

class RangeTyped(TypedDescriptor):
    """Integer descriptor with a range constraint."""
    def __set__(self, obj, value) -> None:
        if hasattr(self, "lo"):
            if value < self.lo:
                raise ValueError(f"{self.name} must be greater than or equal to {self.lo}.")
        if hasattr(self, "hi"):
            if value > self.hi:
                raise ValueError(f"{self.name} must be less than or equal to {self.hi}.")
        super().__set__(obj, int(value))

class PositiveIntTyped(RangeTyped):
    """Positive integer descriptor with no range constraint."""
    def __set__(self, obj, value) -> None:
        super().__set__(obj, abs(int(value)))

class StringTyped(TypedDescriptor):
    """String descriptor with no constraints."""
    pass


# ── Metaclasses ───────────────────────────────────────────────────────────────

def classproperty(method: PropertyFunction[T]) -> property:
    """
    Make a property getter using a function.

    :param method: The function for the getter.
    :return: A ``property`` object bound to `method`.
    """

    return property(operator.attrgetter(method.__name__), doc=method.__doc__)

def instanceproperty(method: PropertyFunction[T]) -> property:
    """
    Make an instance property getter using a function.

    :param method: The function for the getter.
    :return: An ``instanceproperty`` object bound to `method`.
    """

    return property(operator.methodcaller(method.__name__), doc=method.__doc__)

@contextlib.contextmanager
def assert_raises(exc_class: Type[BaseException], message: Optional[str] = ...) -> Generator[None, None, None