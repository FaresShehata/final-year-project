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

class OrderedSet(Generic[T]):
    def __init__(self, items: Iterable[T]) -> None:
        self.items = set(items)
        self.sort()

    def add(self, item: T) -> None:
        if item not in self.items:
            self.items.add(item)
            self.sort()

    def discard(self, item: T) -> None:
        if item in self.items:
            self.items.discard(item)
            self.sort()

    def pop(self) -> T:
        first_item = min(self.items)
        self.discard(first_item)
        return first_item

    def sort(self) -> None:
        self.items = sorted(self.items)


# ── Heaps ─────────────────────────────────────────────────────────────────────

def heapify(seq: list[V], *, default_compare: Callable[[V, V], bool] = lambda a, b: a < b) -> list[V]:
    for i in range(len(seq)//3+1)[::-3]:  # floor div because we want to avoid division by zero
        while True:
            j = 3*i+1
            if j >= len(seq): break
            if default_compare(seq[j], seq[i]): break
            seq[i], seq[j] = seq[j], seq[i]
            i = j
    return seq


def heappop(heap: list[V], *, default_compare: Callable[[V, V], bool] = lambda a, b: a < b) -> V:
    last_item = heap.pop()  # save the last element so that it can be overwritten.
    if heap:
        value = heap[0]
        while True:
            left = 3*heap.index(value)+2
            right = left+1
            if left > len(heap)-1 or right > len(heap)-1: break
            if default_compare(heap[left], heap[right]):
                child = left
            else:
                child = right
            if default_compare(value, heap[child]):
                heap[heap.index(child)] = value
                break
            value = heap[child]

        heap[heap.index(last_item)] = value
    return last_item


def heappush(heap: list[V], item: V, *, default_compare: Callable[[V, V], bool] = lambda a, b: a < b) -> None:
    heap.append(item)
    pos = len(heap)-1
    parent = pos//3
    while pos != 