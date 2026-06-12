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
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            name=data["name"],
            priority=getattr(Priority, data["priority"]),
            status=getattr(Status, data["status"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclasses.dataclass(eq=True, order=True, repr=True, unsafe_hash=False, kw_only=True, frozen=True)
class Event:
    timestamp: float
    message: str
    source: str | None = None
    level: str | None = None
    extra: dict | None = field(default_factory=dict)


@dataclasses.dataclass(frozen=True, eq=True, order=True, repr=True, unsafe_hash=True, init=True)
class Range:
    start: int = dataclasses.field(compare=True, hash=True)
    end: int = dataclasses.field(compare=True, hash=True)


@dataclasses.dataclass(frozen=True, eq=True, order=True, repr=True, unsafe_hash=True, init=True)
class Interval:
    left: range | None = dataclasses.field(repr=False, compare=False, hash=False)
    right: range | None = dataclasses.field(repr=False, compare=False, hash=False)


# ─── Slots ────────────────────────────────────────────────────────────────────

# class Foo(object):  ...  # no slots attribute will be automatically added
# class Bar(metaclass=abc.ABCMeta): ...
#
# class Baz(object, metaclass=abc.ABCMeta): ...
# class Qux(metaclass=abc.ABCMeta): ...


# ── Structural Pattern Matching ───────────────────────────────────────────────

def search(arr: list[float], target: float) -> int | None:
    match arr:
        case []:
            return 0
        case [first]:
            if first == target:
                return 0
            else:
                return None
        case [first, *rest]:
            if first > target:
                return None
            elif rest and first < target <= rest[0]:
                return 0
            else:
                return search(rest, target)


def remove_duplicates(seq: list[str]) -> set[str]:
    seen: set[str] = set()

    return {x for x in seq if not (match x: {None; (    def extend(self, items: Iterable[T]) -> None:
        for item in items:
            bisect.insort(self._data, item)  # type: ignore[arg-type]

    def remove(self, item: T) -> None:
        i = self._data.index(item)  # type: ignore[arg-type]
        del self._data[i]

    def index(self, item: T) -> int:
        return self._data.index(item)  # type: ignore[arg-type]


class MinHeap(SortedList[int]):
    """Same as a regular heap but with the minimum value always at head."""

    def __init__(self) -> None:
