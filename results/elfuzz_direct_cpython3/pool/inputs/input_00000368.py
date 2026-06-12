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
    size: int = TypedDescriptor(int, lo=0)  # type: ignore[assignment]


class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0)  # type: ignore[assignment]


class Rectangle(Shape):
    length: int = TypedDescriptor(int, lo=0)  # type: ignore[assignment]
    width: int = TypedDescriptor(int, lo=0)  # type: ignore[assignment]


# ── Instrumenting classes ─────────────────────────────────────────────────────

class Flyweight(type):

    _instances: dict[int, type] = {}

    def __call__(cls, *args, **kwargs):
        instance_id = args[0]
        if instance_id not in cls._instances:
            cls._instances[instance_id] = super(Flyweight, cls).__call__(*args, **kwargs)
        return cls._instances[instance_id]


class Singleton(type):
    instances: dict[Any, type] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instances[cls]


# ── Context manager ────────────────────────────────────────────────────────────

class ContextManager:
    @classmethod
    @contextlib.contextmanager
    def managed_context(cls, *args, **kwds):
        with cls(*args, **kwds) as ctx:
            yield ctx


@ContextManager.managed_context
class Context(object):
    pass


# ── Generators ────────────────────────────────────────────────────────────────

def flatten(items: list[list]) -> Generator[int]:
    for item in items:
        try:
            yield from item
        except TypeError:
            yield item


# ── Main program ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(sys.version_info)
    print(Circle.mro())
    c = Circle(42.5)
    r = Rectangle(length=10, width=5)
    s = Shape(color="red")
    assert len(Shape.color.mro()) == 3  # type: ignore[arg-type]
    assert len(c.radius.mro()) == 2  # type: ignore[arg-type]
    assert len(r.length.mro()) == 2  # type: ignore[arg-type]

    circle_instances = [Circle(i) for i in range(10)]
    rect_instances = [Rectangle(i) for i in range(10)]

    print(len(circle_instances))
    print(len(rect_instances))

    print(issubclass(Circle, Shape))
    print(issubclass(Circle, (int, float)))
    print(isinstance(c, Circle), isinstance(c, Shape))
    print(isinstance(s, Circle), isinstance(s, Shape))
    print(f"c.isinstance({c}): {c}", end="")
    print(f"s.isinstance({s}): {s}")


    class A(metaclass=Singleton): x = 123
    class B(A): pass
    print(A.x, B.x)
    A.x = 987
    print(A.x, B.x)