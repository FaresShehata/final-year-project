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


# ─── Classes ───────────────────────────────────────────────────────────────────


@count_calls
class Point:
    x: int
    y: int

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<Point ({self.x},{self.y})>"

    def distance_from_origin(self):
        return (self.x**2 + self.y**2)**.5


@count_calls
class TimePoint(Point):
    hour: int
    minute: int

    def __init__(self, hour, minute, x=0, y=0):
        super().__init__(x, y)
        self.hour = hour
        self.minute = minute

    def time_to_edf(self):
        return (60 * self.hour + self.minute - 8 * 60) % (24 * 60)

    def __str__(self):
        return (
            f"@ {self.hour}:{self.minute:02d}\n"
            f"x = {self.x:.2f}\ny = {self.y:.2f}\ndist={super().distance_from_origin():.2f}")


class PointMeta(type):
    _instances: dict[int, Point] = {}

    def __call__(cls, x=0, y=0):
        try:
            instance = cls._instances[id(cls)]
        except KeyError:
            instance = super().__call__(x=x, y=y)
            cls._instances[id(cls)] = instance
        return instance

    def clear_instances():
        cls._instances.clear()

    def __del__(cls):
        del cls._instances[id(cls)]

    def __repr__(cls):
        return f'<{cls.__name__}(x={},y={})>'.format(**vars(cls))


class PointInstance(metaclass=PointMeta):

    x: int
    y: int

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class PointClass:

    x: int
    y: int

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return "<{}>".format(self.__class__.__qualname__)


class PointStatic:

    assert str(bool(0)) == 'False'
    assert isinstance(bool(0), bool)

    assert all([True])
    assert any([True])
    assert not all([])
    assert not any([])

    assert sorted(((), (), ('a',))) == [('a'), ()]
    assert sorted(('()'), key=len) == [()]

    assert range(10)[:5] == range(0, 5)
    assert list(range(10)[:5]) == [0, 1, 2, 3, 4]

    assert zip([(1,), (2,)], [(3,), (4,)]) == ((1, 3), (2, 4))
    assert set(zip([(1,), (2,)], [(3,), (4,)])) == {tuple(x) for x in zip([(1,), (2,)], [(3,), (4,)])}
    assert tuple(zip([(1,), (2,)], [(3,), (4,)])) == ((1, 3), (2, 4))

    assert map(lambda x: x, []).next