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
            "id":       self.id,
            "name":     self.name,
            "priority": self.priority.value,
            "status":   self.status.value,
            "tags":     self.tags,
            "metadata": self.metadata,
            "history":  self._history,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Task:
        return cls(
            id=d["id"],
            name=d["name"],
            priority=Priority(d["priority"]),
            status=Status(d["status"]),
            tags=d.get("tags", []),
            metadata=d.get("metadata", {}),
        )


# ── Slots ────────────────────────────────────────────────────────────────────

class NamedPoint:
    __slots__: tuple[str, ...] = ("_name", "_point")
    _name: str
    _point: Point

    def __init__(self, name: str, point: Point):
        self._name = name
        self._point = point

    @property
    def name(self) -> str:
        """The name of the point."""
        return self._name

    @property
    def point(self) -> Point:
        """The coordinates of the point."""
        return self._point

    def distance_from(self, other: NamedPoint) -> float:
        return self.point.distance(other.point)


# ── Structural Pattern Matching ───────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Book(Generic[T]):
    title: str
    pages: T

def match_book(book: Book[int]) -> None:
    match book:
        case Book(title="Python Essential Reference", pages=1039):
            print("This book has exactly 1039 pages.")
        case Book(_, pages=pages):
            if pages > 800:
                print("There are too many pages.")
            elif pages < 400:
                print("That's not a very long book.")
        case Book(title=f"{title}"):
            print(f"Book title starts with '{title[:3]}'.")
        case _:
            print("I don't know what kind of book this is.")

match_book(Book("Python Essential Reference", 1039))
match_book(Book("Learning Python", 751))
match_book(Book("Introduction to Algorithms", 1364))


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def factorial(n: int) -> int:
    result: int = 1
    i: int = 2
    while i <= n:
        result *= i
        await asyncio.sleep(0.001)
        i += 1
    return result

async def main():
    for n in range(1000, 1010):
        start_time = time.perf_counter()
        result = await factorial(n)
        end_time = time.perf_counter()
        elapsed_time_sec = round(end_time - start_time, 3)
        print(f"n={n:<4}: Result = {result}, Elapsed Time [{elapsed_time_sec:.3f}] sec")


# ── Generics ─────────────────