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
        self._data: list[tuple[int, K]] = []
        for n, item in enumerate(sorted(iterable)):
            self.insert(n, item)

    def insert(self, index: int, value: K) -> None:
        bisect.insort_left(self._data, (index, value))
        while self._data and self._data[-1][0] != index:
            _, v = self._data.pop()
            self.insert(index, v)

    def find(self, index: int) -> Optional[K]:
        i = bisect.bisect_right(self._data, (index, sys.maxsize))
        if i > 0:
            i -= 1
        return self._data[i][1]

    def remove(self, index: int) -> None:
        i = bisect.bisect_right(self._data, (index, sys.maxsize))
        if i >= len(self._data):
            raise ValueError(f"{index} not found.")
        _, v = self._data.pop(i)
        while self._data and self._data[-1][0] < index:
            _, v = self._data.pop()

    def __getitem__(self, index: Union[slice, int]) -> Union[List[K], K]:
        if isinstance(index, slice):
            return [v for k, v in self._data[index]]
        else:
            return self.find(index)

    def __setitem__(self, index: int, value: K) -> None:
        del self[index]
        self.insert(index, value)

    def __delitem__(self, index: Union[slice, int]) -> None:
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            for i in range(stop)[::-step or 1]:
                self.remove(start + i)
        else        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

