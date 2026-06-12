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

    def __init__(self, iterable=None, *, reverse=False):
        super().__setattr__("reverse", reverse)
        if iterable is not None:
            self.extend(iterable)

    def __repr__(self) -> str:
        return f"SortedList({list(self)})"

    def __str__(self) -> str:
        return f"[{', '.join(str(e) for e in self)}]"

    def __iter__(self):
        return iter(sorted(self, reverse=self.reverse))

    def __len__(self):
        return len(sorted(self, reverse=self.reverse))

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            return type(self)(sorted(self[start:stop:step], reverse=self.reverse))
        else:
            return next(islice(sorted(self, reverse=self.reverse), idx, idx+1))

    def __contains__(self, obj):
        i = bisect.bisect_left(self, obj, lo=-1, hi=len(self)-1)
        return i != len(self) and (not self.reverse or self[i] == obj)

    def count(self, value):
        i = bisect.bisect_left(self, value, lo=-1, hi=len(self)-1)
        j = bisect.bisect_right(self, value, lo=i, hi=len(self))
        return j-i

    def index(self, value, *, lo=0, hi=None):
        if lo < 0:
            raise ValueError(f"lower bound must be non-negative not {lo}")
        elif not self.reverse:
            i = bisect.bisect_left(self, value, lo=lo, hi=hi)
        else:
            i = bisect.bisect_right(self, value, lo=lo, hi=hi)
        if i == len(self) or self[i] != value:
            raise ValueError(f"{value} is not in list")
        return i

    def append(self, obj):
        bisect.insort(self, obj, lo=-1, hi=len(self)-1)

    def extend(self, values):
        insort_lh(self, *values, lo=-1, hi=len(self)-1, reverse=self.reverse)

    def pop(self, idx=-1):
        del self[idx]

    def remove(self, value):
        i = self.index(value)
        del self[i]


