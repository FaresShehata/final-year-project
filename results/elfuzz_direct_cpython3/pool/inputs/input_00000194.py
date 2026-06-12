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
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self.container: list[T] = []

    def add(self, value: T) -> None:
        idx = bisect.bisect_left(self.container, value)
        self.container.insert(idx, value)

    def remove(self, value: T) -> None:
        idx = bisect.bisect_left(self.container, value)
        if idx < len(self.container) and self.container[idx] == value:
            del self.container[idx]

    def discard(self, value: T) -> None:
        try:
            self.remove(value)
        except ValueError:
            pass

    def pop(self) -> T:
        return self.container.pop()

    def clear(self) -> None:
        del self.container[:]

    def __contains__(self, item: T) -> bool:
        idx = bisect.bisect_left(self.container, item)
        return idx < len(self.container) and self.container[idx] == item

    def __len__(self) -> int:
        return len(self.container)

    def __getitem__(self, i: int) -> T:
        return self.container[i]

    def __repr__(self) -> str:
        return f"<SortedList({self.container})>"


# ── Deque with max size ───────────────────────────────────────────────────────


def queue_with_max_size(size: int) -> deque[tuple[float, float]]:
    """
    Returns a double-ended queue that enqueues elements into a heap of at most
    `size` items by default.

    If the queue is full when adding an item, the oldest element will be removed.
    """

    class QueueWithMaxSize(deque[float]):
        def append(self, item: tuple[float, float]) -> None:
            if len(self) >= size:
                self.popleft()
            super().append(item)

    return QueueWithMaxSize()


# ── Counters ─────────────────────────────────────────────────────────────────

counter = Counter(["a", "b", "a"])


# ── Defaultdict ───────────────────────────────────────────────────────────────

defaultdict(int)["a"] += 1


# ── Dataclasses and slots ─────────────────────────────────────────────────────

point = Point(x=3.4, y=6.789)


# ── Structural Pattern Matching ───────────────────────────────────────────────


class Cat:
    def meow(self) -> str: return "meow!"
   
# ── Async machinery ───────────────────────────────────────────────────────────

