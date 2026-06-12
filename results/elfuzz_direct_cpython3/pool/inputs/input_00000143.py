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

    def __set__(self, obj: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"'{value}' must be '{self.expected_type}'")
        elif (self.lo is not None and value < self.lo) or \
                (self.hi is not None and value > self.hi):
            raise ValueError(
                    f"{value} not in allowed range ["
                    f"{self.lo}, {self.hi}]")
        setattr(obj, self.name, value)


class IntegerTyped(TypedDescriptor):
    """Integer Descriptor with an int instance."""

    def __set__(self, obj: T, value: Any) -> None:
        value = super().__set__(obj, value)
        if isinstance(value, float) and round(value) != value:
            raise TypeError("'{}' must be integer".format(self.name))
        return value


class FloatTyped(TypedDescriptor):
    """Float Descriptor with a float instance."""

    pass


class StrLengthTyped(TypedDescriptor):
    """Str Length Descriptor with a str length instance."""

    def __set__(self, obj: T, value: Any) -> None:
        value = super().__set__(obj, value)
        if len(value) == 0:
            raise TypeError(
                    "'{}' must have non-empty string".format(self.name))
        return value


# ─── Classes ───────────────────────────────────────────────────────────────────

class Point2D:
    """Point in 2D space."""

    x: int = IntegerTyped(int, -500, 500)
    y: int = IntegerTyped(int, -500, 500)

    def __init__(self, x: int=0, y:int=0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return "<Point({:.3f},{:.3f})>".format(self.x, self.y)

    @classmethod
    def zero(cls) -> Point2D:
        """Alternate constructor for the origin point."""
        return cls(0.0, 0.0)

    @property
    def distance_to_origin(self) -> float:
        """Return Euclidean distance from current point to origin."""
        from math import