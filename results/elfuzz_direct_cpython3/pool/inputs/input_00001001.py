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
    CANCELED  = "canceled"

@runtime_checkable
class AsyncIterable(Protocol[K], Generic[K]):
    def __aiter__(self) -> AsyncIterator[K]:
        ...

async def collect(iterables: Iterable[AsyncIterable[T]]) -> list[T]:
    return [item async for iterable in iterables for item in iterable]

def flatten(iterable: Iterable[Iterable[V]]) -> Iterator[V]:
    """Flatten an arbitrarily nested sequence of values."""
    for item in iterable:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, order=True)
class User():
    id: int
    name: str = None
    age: float = 1.25

    @classmethod
    def from_dict(cls, mydict: dict[str, object]) -> User:
        return cls(**mydict)

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.age}"

user = User.from_dict({
    "id": 101,
    "name": "Alice",
    "age": 34.7
})

print(user.full_name)

# ─── Slots ──────────────────────────────────────────────────────────────────

class MySlotClass(metaclass=abc.ABCMeta):
    __slots__ = ["x", "y"]

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def method(self):
        print("in method")

s = MySlotClass(1, 2)
print(s.__slots__)
try:
    s.z = 3
except AttributeError as e:
    print(e)

@dataclasses.dataclass(eq=False)
class MyClass:
    x: int
    y: int

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(
                f"'==' not supported between instances of '{type(self).__qualname__}' and "
                f"'{type(other).__qualname__}'",
            )
        return self.x == other.x and self.y == other.y


# ─── Structural Pattern Matching ────────────────────────────────────────────

class Shape(Generic[T]):
    def area(self) -> T:
        ...
