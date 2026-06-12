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
        self.sort_key = hash(tuple(sorted(self.tags)))

    def update_status(self, status: Status) -> None:
        if status.is_terminal():
            while len(self._history) > 0 and not self._history[-1].is_terminal():
                del self._history[-1]
            
            self._history.append(status)

        assert len(self._history) <= 3
        
        if status == Status.RUNNING:
            self.status = Status.RUNNING
        elif status == Status.SUCCESS:
            self.status = Status.SUCCESS
        else:
            raise ValueError(f"Invalid status: {status}")

    @property
    def history(self) -> list[Status]:
        return [*self._history]

    def merge(self, other: Task) -> Task:
        task = Task(
            id       = self.id,
            name     = self.name,
            priority = min(self.priority, other.priority),
            status   = self.status,
            tags     = sorted(set(list(self.tags) + list(other.tags))),
            metadata = {},
        )

        task.update_status(Status.SUCCESS)
        return task


def add_tags(task: Task, *tags: str) -> Task:
    task.tags.extend(tags)
    task.sort_key = hash(tuple(sorted(task.tags)))
    return task


def merge_tasks(tasks: list[Task]) -> Task:
    tasks.sort(key=lambda t: t.priority)
    
    res = tasks.pop(0).merge(tasks.pop(0))
    for task in tasks:
        res.merge(task)

    return res


# ── Generics ──────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)


class AbstractCollection(Generic[T_co]):
    async def add(self, item: T_co) -> None: ...
    async def pop(self) -> T_co: ...
    

class OrderedSet(AbstractCollection[int]):
    def __init__(self, iterable=None):
        self.heap: list[tuple[float, int]] = []
        self.dict: dict[int, tuple[float, int]] = {}
        
        if isinstance(iterable, Iterable):
            await self.add_many(iterable)

    async def add_many(self, iterable: Iterable[int]) -> None:
        for i in iterable:
            await self.add(i)

    async def add(self, item: int) -> None:
        if item in self.dict:
            _, old_i = self.dict[item]
            ind = bisect.bisect