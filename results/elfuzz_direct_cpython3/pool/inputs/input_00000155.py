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
    FAILED    = "failed"
    CANCELLED = "cancelled"
    DONE      = "done"


class ShapeType(enum.Enum):
    TRIANGLE     = "triangle"
    SQUARE       = "square"
    RECTANGLE    = "rectangle"
    CIRCLE       = "circle"
    ELLIPSE      = "ellipse"
    PARALLELOGRAM = "parallelogram"
    HEPTAGON     = "heptagon"
    OCTAGON      = "octagon"
    NONAGON      = "nonagon"
    DECAGON      = "decagon"
    HUNDRED_GON  = "100-gon"


# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Person:

    age: int
    name: str
    email: str | None = None

    # This definition of `mails` makes it impossible to use the fast `in`
    # operation on `set`, but allows for efficient lookups with `get`.
    mails: set[str] = dataclasses.field(default_factory=set)

    def full_name(self) -> str:
        return f"{self.name} {self.age}"


# ── Decorators ───────────────────────────────────────────────────────────────-

def memoize(func: Callable[..., T]) -> Callable[..., T]:
    cache: dict[K, V] = {}

    @overload
    def decorator(_: Callable[..., T]) -> Callable[..., T]: ...
    
    @overload
    def decorator(v: K) -> Callable[[Callable[..., T]], Callable[..., T]]: ...
        
    def decorator(v=None) -> Callable[[Callable[..., T]], Callable[..., T]]:
        nonlocal cache
        
        if v is None:
            return lambda func: decorator(func)
            
        return functools.wraps(func)(
            lambda *args, **kwargs: cache.setdefault(v, func(*args, **kwargs))
        )
    
    return decorator


# ── Generics ──────────────────────────────────────────────────────────────────

class FrozenDict(Generic[T], abc.Mapping[T, Any]):
    
    def __init__(self, mapping: Mapping[T, Any]): 
        self._mapping = {}
        self.update(mapping)
    
    def update(self, mapping: Mapping[T, Any]): ... 
        
    def copy(self): ... 

    def __getitem__(self, key) -> Any: raise KeyError        return f"<class '{cls.__qualname__}' via RegistryMeta>"


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
