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


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=getattr(Priority, data["priority"]),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    sex: str = dataclasses.field(compare=False)


@dataclasses.dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclasses.dataclass(frozen=True)
class Point3D(Point2D):
    z: float


# ── Generics and type hints ───────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    return a + b


def check(a: T, b: T) -> T:
    if a == b:
        raise ValueError("a and b are equal")
    else:
        return a


def foo(x: T) -> T:
    return x


def bar(x: T) -> T:
    return x


async def baz(x: T) -> T:
    await asyncio.sleep(random.random())
    return x


def qux(x: T) -> T:
    return x


def coro() -> Callable[[Awaitable[T]], Awaitable[T]]:
    ...


async def main() -> None:
    assert add(1, 2) == 3
    assert check(42, 42) == 42
    assert foo(bar(0)) == 0
    assert foo(await baz(qux(0))) == 0

    print(add(1, 2))
    print(check(42, 42))
    print(foo(bar(0)))
    print(foo(await baz(qux(0))))

# ── Walrus operator ───────────────────────────────────────────────────────────

print(time.perf_counter())

print((t := time.perf_counter()))

while t < time.perf_counter():
    print(t := time.perf_counter())


# ── Structural Pattern Matching ───────────────────────────────────────────────

s = "hello world"
match s:
    case "hello":
        print("Greetings, hello!")
    case "goodbye":
        print("Farewell, goodbye!")
    case _:

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

