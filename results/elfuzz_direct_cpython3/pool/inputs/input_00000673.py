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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(
                f"Got {val!r}, which exceeds the range ({self.hi}) "
            )

        setattr(obj, self.name, val)


def typed(name: str) -> type:
    """
    Returns a new descriptor class with a single attribute named after self.

    The attribute is set by setting an instance of this descriptor on the target
    object. This can be done using the dot notation, or through calling it as a
    function (and passing the instance as first argument).

    >>> from pprint import pprint
    >>>
    >>> class Foo(object):
    ...     bar = typed('bar')
    ...
    >>>
    >>> pprint(Foo.bar)
    <some random object>

    If one wants to enforce specific values, they need to define the attributes
    `lo` and `hi`, e.g.

    >>> class Bar(object):
    ...     baz = typed('baz', lo=3, hi=7)
    ...
    >>>
    >>> pprint(Bar.baz)
    <some random object>
    """

    self = TypedDescriptor()
    self.name = ""
    return self


class TypedGenericMeta(type):
    def __new__(mcls, name, bases, namespace):

        attrs = {
            attr: TypedDescriptor() for attr in namespace.keys()
            if not attr.startswith("_")
        }
        return super().__new__(mcls, name, bases, namespace.update(attrs))

    # def __call__(cls, *args, **kwargs):
    #     instance = super().__call__(*args, **kwargs)
    #     for k, v in kwargs.items():
    #         setattr(instance, k, v)

    def __getitem__(cls, args):
        """Returns a subclass of cls that uses the given parameters."""

        if isinstance(args, tuple) and len(args) == 2:
            lo, hi = args

            class New(cls, metaclass=TypedGenericMeta):
                lo = lo
                hi = hi

            return New

        elif isinstance(args, int):
            class New(cls, metaclass=TypedGenericMeta):
                lo = -sys.maxsize
                hi = args

            return New

        else:
            raise ValueError(f"{args} is not valid")


@typed("length")
@typed("width", lo=5)
class Rectangle:

    length: float
    width: float
    area: float

    def __init__(self, length: float, width: float) -> None:
        self.length = length
        self.width = width
        self.area = 0

    @property
    def area(self):
        self.area = self.length * self.width
        return self.area

    @area.setter
    def area(self, value: float) -> None:
        self.length *= value / self.width


def test_rectangle():
    r = Rectangle(length=4, width=3)
    print(r.area)
    r.area = 8
    assert r.length == 6
    print(r.area)


# ─── Abstract Base Classes ──────────────────────────────────────────────────


class ShapeABC(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, target_class):
        if cls is ABCShape and isinstance(target_class, Shape):
            return True
        return NotImplemented

    @abc.abstractmethod
    def area(self):
        pass

    @abc.abstractproperty
    def perimeter(self):
        pass


class Circle(ShapeABC):
    radius: float

    def __init__(self, radius: float):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius**2

    @property
    def perimeter(self):
        return 2 * 3.14 * self.radius


class Square(ShapeABC):
    side