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
class Comparable(Protocol):
    def __lt__(self, _: Any) -> bool:
        ...

# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class Person:
    name: str
    age: int
    height: float = 0.0


person = Person("John Doe", 30, height=1.75)
print(person)
print(p.__dict__)
print(type(p))


@dataclasses.dataclass(frozen=True, slots=True, init=False)
class MyDataClass:
    def __init__(self, a: int):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)


x = MyDataClass(1)
y = MyDataClass(2)

print(x.a)
print(x.b)
#print(x.c)  # error


class Point(Generic[T]):
    def __init__(self, x: T, y: T):
        if isinstance(x, int) and isinstance(y, int):
            raise ValueError("Both coordinates must be integers.")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def __getattribute__(self, __name: str) -> Any:
        if not hasattr(self, __name):
            raise AttributeError(__name)
        return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        raise AttributeError("Cannot modify attributes of this class.")

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


point = Point[float](1.0, 2.0)
print(point.x)



def seed():
    random.seed(42)


T = TypeVar("T")
K = TypeVar("K", contravariant=True)
V = TypeVar("V")


# https://docs.python.org/3/library/typing.html#protocols
class Protocol(Protocol):
    pass


@dataclasses.dataclass(frozen=True)
class Node:
    value: int
    left: Optional[Node] = None
    right: Optional[Node] = None


async def foo() -> None:
    print("foo")


class Foo:
    @classmethod
    async def bar(cls) -> None:
        print("bar")

    @staticmethod
    async def baz() -> None:
        print("baz")


print(foo())
print(Foo.bar())
Foo.baz()


@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int


p = Person(name="John", age=36)
s = {**p}
del p.name
try:
    s["name"]
except KeyError as e:
    print(e)


@dataclasses.dataclass(eq=True)
class Point:
    x: float
    y: float

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y


print(Point(x=1.0, y=2.0) != Point(y=2.0, x=1.0))
print(Point.__hash__)


@dataclasses.dataclass
class Point2:
    x: float
    y: float
    z: float = 0.0


b = Point2(1.0, 2.0, 3.0)
c = Point2(1.0, 2.0, 3.0)

d = Point2(1.0, 2.0, 5.0)

a = c != d
print(a)


@dataclasses.dataclass(order=True)
class NamedPoint(dataclasses.dataclass):
    name: str
    location: Point


n = NamedPoint("A", Point(0, 0))
m = NamedPoint("B", Point(1, 1))

print(n < m)
print(n <= m)
print(m > n)
print(m >=        }


@runtime_checkable
class SearchProtocol(Protocol[K, V]):
    def search(self, key: K) -> V:
        ...


@runtime_checkable
class SortedSearchProtocol(SearchProtocol[K, V]):
    def sort(self, iterable: Iterable[K], reverse=False) -> V:
        ...


@runtime_checkable
class AsyncIterable(Protocol[T]):
    async def __aiter__(self) -> AsyncIterator[T