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
            "priority": self.priority,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "_history": self._history,
        }

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> Task:
        del d["_history"]
        return cls(**d)


# ── Generics ───────────────────────────────────────────────────────────────────

class SortedList(Generic[K]):
    """Implementation of sorted linked-list using binary search."""

    def __init__(self, iterable: Iterable[K] = ()) -> None:
        self._data: list[tuple[int, K]] = []  # [(idx, value)]
        for i, v in enumerate(sorted(iterable)):
            self.insert(i, v)

    def insert(self, index: int, item: K) -> None:
        if not self or index <= len(self):
            bisect.insort(self._data, (index, item))
        else:
            raise IndexError(index)

    def remove(self, item: K) -> None:
        idx = next((i for i, (_, val) in enumerate(self._data) if val == item), None)
        if idx is not None:
            self.remove_at(idx)

    def remove_at(self, index: int) -> K:
        if index < 0 or index >= len(self):
            raise IndexError(index)
        _, removed_item = self._data.pop(index)
        return removed_item

    def pop(self) -> K:
        return self.remove_at(len(self) - 1)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index: int) -> K:
        key = self._data[index][0]
        item = self._data[index][1]
        return item[key]

    def __setitem__(self, index: int, item: K) -> None:
        assert isinstance(item, tuple)
        self._data[index] = (key, item)

    def __iter__(self) -> Iterator[K]:
        return iter(map(lambda _: _.tuple(), self._data))

    def __repr__(self) -> str:
        return f"SortedList({list(self)})"


def split_words(text: str, max_length: int = 64) -> Generator[str, None, None]:
    words = text.split()
    while words:
        yield "".join(words[:max_length])
        words = words[max_length:]


def format_time(seconds: float, precision: int = 3) -> str:
    minutes, seconds = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)
    parts = []
    if years > 0:
        parts.append(f"{years}y")
    if days > 0:
        parts.append(f"{days:d}d")
    if hours > 0:
        parts.append(f"{hours:d