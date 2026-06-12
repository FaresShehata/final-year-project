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
        # If the method is called with an instance, this will be None because
        # we have set `obj=None` in the constructor.
        cache = obj._cache
        if self.attrname:
            cache = cache.setdefault(self.attrname, {})
        result = cache.get(self)
        if result is None:
            result = cache[self] = self.func(obj)
        return result


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.cnt += 1
        print(wrapper.cnt, ":", end=" ")
        return func(*args, **kwargs)

    wrapper.cnt = 0
    return wrapper


@count_calls
def factorial(n: int) -> int:
    """Calculate n! (factorial of n)."""

    if n < 0 or not isinstance(n, int):
        raise ValueError("n must be a non-negative integer.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(5))
print(factorial.cnt)


# ─── Property Decorator ──────────────────────────────────────────────────────


class Point:
    _x: float
    _y: float

    def __init__(self, x=0.0, y=0.0):
        self.set_x(x)
        self.set_y(y)

    def get_x(self) -> float:
        return self._x

    def set_x(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError("'float' expected")
        self._x = value

    def del_x(self) -> None:
        del self._x

    def get_y(self) -> float:
        return self._y

    def set_y(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError("'float' expected")
        self._y = value

    def del_y(self) -> None:
        del self._y

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self.set_x(value)

    @x.deleter
    def x(self) -> None:
        self.del_x()

    @