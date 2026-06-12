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

    @CachedProperty
    def area(self) -> float:
        return 0.0

    def __str__(self) -> str:
        return f"The {self.area} square shape."


# ─── Concrete implementation ──────────────────────────────────────────────────

@dataclasses.dataclass
class Circle(Shape):

    radius: float = TypedDescriptor(float, 0, 1e6)
    pi: float = TypedDescriptor(float, 1, 4)

    @cached_property
    def area(self) -> float:
        return math.pi * self.radius**2


class Rectangle(Shape):
    width: float = TypedDescriptor(float, 0, 1e6)
    height: float = TypedDescriptor(float, 0, 1e6)

    def __post_init__(self):
        self.width = min([self.height, self.width])

    @property
    def area(self) -> float:
        return self.width * self.height


# ─── Factory method ───────────────────────────────────────────────────────────

class ShapeFactory:
    shapes: list[type[Shape]] = []

    @classmethod
    def register(cls, shape_cls: type[Shape]) -> None:
        assert shape_cls in cls.shapes, f"{shape_cls.__name__} already registered"
        cls.shapes.append(shape_cls)

    @classmethod
    def create(cls, name_or_id: int | str) -> Shape:
        for shape_class in cls.shapes:
            try:
                id_attr = shape_class.id_attr
            except AttributeError:
                continue
            if hasattr(shape_class, id_attr) and getattr(shape_class, id_attr) == name_or_id:
                return shape_class()
        raise ValueError(f"No such shape named or identified as {name_or_id}")


class ShapeAbstractFactory(metaclass=abc.ABCMeta):
    class InvalidIdError(ValueError):
        pass

    def __init__(self):
        self.shape_dict: dict[int, type[Shape]] = {}
        self.id_counter: int = 0

    def register_shape(self, shape_cls: type[Shape], id_: int) -> None:
        if id_ in self.shape_dict:
            raise KeyError(id_)
        self.shape_dict[id_] = shape_cls
        shape_cls.id_attr = id_
        self.shape_dict[id_] = shape_cls

    def unregister_shape(self, shape_cls: type[Shape]) -> None:
        del self.shape            print("First!")
        case {"id": 2}:
            print("Second!")
        case {"id": 3}:
            print("Third!")
        case {"name": name} if len(name) < 5:
            print(f"Short name: {name}")
        case {"price": p} if type(p) != int:
            print(f"Not an integer: {p}")
        case {"id": i,