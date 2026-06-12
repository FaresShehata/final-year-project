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


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ── Decorators ────────────────────────────────────────────────────────────────

def typed_property(name: str, expected_type: type[T]) -> T:
    storage_name: str = "_" + name
    
    @property
    def prop(self: T) -> T:
        return getattr(self, storage_name)

    @prop.setter
    def prop(self: T, value: T) -> None:
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type}")
        setattr(self, storage_name, value)
        
    return prop

@dataclasses.dataclass(order=True)
class MyDataClass:
    first_name: str
    last_name: str
  
  # this will work as well for private attributes
    _age: int
  
  
  # these properties are also available
    @typed_property('first_name', str)
    def first_name(self) -> str:
      pass
  
  # these properties are also available
    @typed_property('_age', int)
    def age(self) -> int:
      pass


@functools.total_ordering
@dataclasses.dataclass(order=True)
class Item(Generic[K]):
    key: K
    value: V

    def __post_init__(self) -> None:
        self.latest_value: Optional[V] = None

    
# ── Classes ───────────────────────────────────────────────────────────────────

class Queue(Generic[K], Iterable[K], Sized, Container[K]):
    """Implement a queue using a Python list."""
    def __init__(self) -> None:
        self.queue: List[K] = []
    
    def enqueue(self, item: K) -> None:
        self.queue.append(item)
    
    def dequeue(self) -> K:
        if len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            raise IndexError("Cannot pop from an empty queue.")
    
    def size(self) -> int:
        return len(self.queue)


class Cache(dict, Generic[K,V]):
    """Custom implementation of a thread-safe LRU cache with a maxsize.
    """
    def __init__(self, maxsize: int = 128) -> None:
        super().__init__()
        self.maxsize = maxsize
        self.peeked: Dict[K,Timedelta] = {}
        self.hits: Dict[K,int] = {}
        self.touched: Set[K] = set()
        self.misses: int = 0class CachedProperty:
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
    
    def __bool__(self) -> bool:
        return True
    
    
# ── Concrete classes ───────────────────────────────────────────────────────────

class Square(Shape):

    side_length: float = TypedDescriptor(float, 2 <= ...)

    def __init__(
        self,
        side_length: float = 1,
        color: str = "green",
    ):
        super().__init__(color=color)
