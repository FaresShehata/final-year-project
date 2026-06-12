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
        elif self.lo is not None and self.lo > value:
            raise ValueError(f"{self.name}: too low")
        elif self.hi is not None and self.hi < value:
            raise ValueError(f"{self.name}: too high")
        setattr(obj, self.name, value)


@functools.total_ordering
class Shape:
    color: str = Descriptor("str", lo="black")  # type: ignore[argument-mismatch]
    hidden: bool = Descriptor(bool)
    visible: bool = PropertyDelegate("hidden", "visible")

    def __init__(self, color: str = "red"):
        self.color = color

    @property
    def width(self) -> float:
        return self.height

    @width.setter
    def width(self, value: float) -> None:
        self.height = value

    def area(self) -> float:
        return self.width * self.height


class Descriptor:
    """
    A descriptor example from the book.

    >>> d = Descriptor('string')
    >>> print(d.value)
    string
    >>> d.value = 'changed'
    >>> print(d.value)
    changed
    """

    def __init__(self, name: str = "") -> None:
        self.name = name

    def __get__(self, instance: Any, cls: Optional[type]) -> Any:
        if instance is None:
            return self
        else:
            return getattr(instance, self.name)

    def __set__(self, instance: Any, value: Any) -> None:
        setattr(instance, self.name, value)


class PropertyDelegate:
    """
    A property delegate example from the book.

    >>> class SomeClassWithProperties:
    ...     some_property = Delegate('some_attribute', 'some_method')

    >>> scwp = SomeClassWithProperties()
    >>> scwp.some_property = 42
    >>> scwp.some_property
    42
    >>> scwp._SomeClassWithProperties__some_attribute
    42
    >>> scwp.some_method()
    42
    """

    def __init__(
        self,
        attribute_name: str,
        method_name: str,
        default: Optional[Any] = None,
        doc: Optional[str] = None,
    ) -> None:

        self.attribute_name = attribute_name
        self.method_name = method_name
        self.default = default
        self.doc = doc or f"Property delegating to `{method_name
    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
