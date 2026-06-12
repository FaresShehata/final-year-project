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
            raise TypeError(f"{value!r} must be of type {self.expected_type}")
        if self.lo is not None and value < self.lo or self.hi is not None and value > self.hi:
            raise ValueError(
                f"value {value!r} must be in the range [{self.lo}, {self.hi}]"
            )
        setattr(obj, self.name, value)


def int_range(lo=None, hi=None):
    """
    Create a descriptor enforcing an integer range.

    Arguments are passed to ``TypedDescriptor``.
    """

    class IntRange(TypedDescriptor):
        expected_type = int

    return IntRange(lo=lo, hi=hi)


T_co = TypeVar("T_co", covariant=True)
S = TypeVar("S")


class StringEnum(str, enum.Enum):
    pass


class StrEnum(StringEnum):
    def __new__(cls, *values: Any, **kwargs: Any) -> "StrEnum":
        obj = super().__new__(cls, values[0])
        obj._value_ = values[0]
        for v in values[1:]:
            if v != cls(v)._value_:
                raise ValueError(f"All choices must have the same string value")
        obj.value = values[0]
        return obj


@dataclass(unsafe_hash=True)
class Point2D:
    x: float
    y: float


Point3D = dataclasses.make_dataclass(
    "Point3D",
    ["x", "y", "z"],
    namespace={"__post_init__": lambda self: print(self)},
)


class SingletonMeta(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:

        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwds)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """A singleton example."""

    def hello(self):
        print("Hello")


class DuckType:
    def quack(self):
        ...


class ConcreteDuck(DuckType):
    def fly(self):
        ...


def main() -> None:
    """"""

    # 1. Methods: Abstract Base Classes
    print()
    print("-" * len("Methods: Abstract Base Classes"))
   