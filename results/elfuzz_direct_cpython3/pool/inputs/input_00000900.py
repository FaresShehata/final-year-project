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

    @property
    def width(self) -> int:
        return 10

    @width.setter
    def width(self, value):
        pass

    @width.deleter
    def width(self):
        del self.width

    @property
    def height(self) -> int:
        return 15

    @height.setter
    def height(self, value):
        pass

    @height.deleter
    def height(self):
        del self.height

    @staticmethod
    def get_instance(name: str) -> Shape:
        """
        Return the singleton instance for this shape.

        Raises:
          KeyError -- If no such shape exists.
        """
        return RegistryMeta._registry.get(name.lower())


@Shape.register
class Circle(Shape):

    radius: float = TypedDescriptor(float, lo=0.0, hi=sys.float_info.max)

    def __init__(self, radius: float = 1.0, *, color="red") -> None:
        super().__init__(color=color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2

    def perimeter(self) -> float:
        return math.pi * self.radius * 2

    @classmethod
    def from_area(cls, area: float) -> Circle:
        radius = math.sqrt(area / math.pi)
        return cls(radius=radius)

    @classmethod
    def from_perimeter(cls, perimeter: float) -> Circle:
        radius = perimeter / (2 * math.pi)
        return cls(radius=radius)

    def __eq__(self, other):
        return (
            isinstance(other, Circle)
            and self.radius == other.radius
            and self.color == other.color
        )


Circle.register(Square)  # register Square explicitly


@Shape.register
class Rectangle(Shape):

    width: int = TypedDescriptor(int, lo=0, hi=_MAX_INT)
    height: int = TypedDescriptor(int, lo=0, hi=_MAX_INT)

    def __init__(
        self,
        width: int,
        height: int,
        *,
        color="black",
        corner_color="blue",
    ) -> None:
        super().__init__(color=color)
        self.corner_color = corner_color
        self.width = width
        self.height = height

    def area(self) -> int:
        return self.width * self.height

    def perimeter(self) -> int:
        return (self.width +        cls.__bases__[1].__bases__ = (object,)
        return cls

    def __new__(mcs, name, bases, attrs, **kwargs):
        # Check for an explicit constructor.
        init = attrs.pop("__init_subclass__", None)
        if init is None:
            # No constructor provided. Use default behavior.
            return super().__new__(mcs, name, bases, attrs, **kwargs)
        else:
            # Define a new constructor that calls the superclass's one first.
            # This will ensure the registry is properly initialized.
            def __init__(cls, **kwargs):
                init(cls, **kwargs)
                cls._registry.append(cls)
            # Add the new constructor to our subclass dictionary.
            attrs["__init__"] = __init__

        # Initialize the registry list as a class variable.
        if "__slots__" in attrs:
            attrs["__slots__"].append("_registry")
        else:
            attrs["_registry"] = []

        # Create the class using the superclass's __new__ method.
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        return cls

    def __call__(cls, *args, **kwargs):
        """Call the specified subclass constructor."""
        instance = super().__call__(*args, **kwargs)
        for subcls in cls._registry:
            if subcls is not instance:
                subcls.instances.append(instance)
        return instance


class AbstractClass(metaclass=RegistryMeta):
    """Abstract base class with a registry for its instances."""

    instances: list[Any]
    _registry: list[Type[AbstractClass]]

    def __init_subclass__(cls, **kwargs):
