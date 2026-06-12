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
    def area(self): ...

    @classmethod
    def register(cls, shape_cls: Type["Shape"]) -> Type["Shape"]:
        """Class decorator to register concrete subclasses."""
        assert inspect_abstract(shape_cls), (
            "Can only decorate abstract classes with Shape.register()."
        )

        cls._registry[shape_cls.__name__.lower()] = shape_cls
        return shape_cls

    @CachedProperty
    def perimeter(self) -> float:
        """Compute the perimeter, using cached values for width and height."""
        return (self.width + self.height) * 2


@Shape.register
class Circle(Shape):
    radius: float = TypedDescriptor(float)
    pi = 3.14159

    def area(self) -> float:
        return self.pi * self.radius**2

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @diameter.setter
    def diameter(self, diameter: float) -> None:
        self.radius = diameter / 2

    @cached_property
    def circumference(self) -> float:
        return 2 * self.pi * self.radius



# ── Context manager ───────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress_exception(*exceptions):
    try:
        yield
    except exceptions as e:
        print(e)


# ── Generators ───────────────────────────────────────────────────────────────-

def memoize(func):
    memo = {}
    def helper(x):
        try:
            return memo[x]
        except KeyError:
            result = func(x)
            memo[x] = result
            return result
    return helper


def map_async(iterable, map_func, chunksize=16) -> list[Any]:
    results = []
    iterable = iter(iterable)
    while True:
        try:
            args = tuple(itertools.islice(iterable, chunksize))
            if not args:
                break
            results.extend(map_func(*args))
        except StopIteration:
            break
    return results


def concurrent_map(func, items, *, workers=8, maxsize=16):
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=maxsize)
    futures = [pool.submit(func, item) for item in items]
    for future in concurrent.futures.as_completed(futures):
        yield future.result()


# ── Main code ────────────────────────────────────────────────────────────────

if