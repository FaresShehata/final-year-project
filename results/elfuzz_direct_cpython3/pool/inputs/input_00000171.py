"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20

    def __str__(self) -> str:
        return f"priority{self.value}"


# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:

    first_name: str
    last_name: str | None = None
    age: int | None = None

    @classmethod
    def from_json(cls, s: str) -> Person:
        d = json.loads(s)
        for k, v in d.items():
            setattr(cls, k, v)
        return cls(**d)


class Base:
    abc_attr: str | None

    def method_a(self, arg: str) -> str:
        return f"a-{arg}"

    @property
    def property_a(self) -> str:
        return ""

    @Base.property_a.setter
    def property_a(self, value: str) -> None:
        pass

    @staticmethod
    def static_method_a(arg: str) -> str:
        return "a-" + arg

    @classmethod
    def class_method_a(cls, arg: str) -> str:
        return "a-" + arg


class Derived(Base):

    abc_attr: str | None

    def method_b(self, arg: str) -> str:
        return f"b-{arg}"

    @property
    def property_b(self) -> str:
        return ""

    @Derived.property_b.setter
    def property_b(self, value: str) -> None:
        pass

    @staticmethod
    def static_method_b(arg: str) -> str:
        return "b-" + arg

    @classmethod
    def class_method_b(cls, arg: str) -> str:
        return "b-" + arg


# ── Decorators ───────────────────────────────────────────────────────────────-

def check_type(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        for name, value in bound_args.arguments.items():
            expected_types = getattr(
                func, "_expected_types_", {}
            ).get(name)
            if expected_types is not None:
                assert isinstance(value, expected_types), f"Expected {value} to be an instance of {expected        cache = obj.__dict__
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
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

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
