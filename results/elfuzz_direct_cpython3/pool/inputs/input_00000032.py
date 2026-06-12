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
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def extend(self, items: Iterable[T]) -> None:
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
        super().__init__()
        heapq.heapify(self._data)

    def pop_min(self) -> int:
        return heapq.heappop(self._data)


assert all(i == v for i,v in enumerate(MinHeap().pop_min() for _ in range(3))), "MinHeap fails."


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class FrozenPoint(Point): ...

print(FrozenPoint.__slots__)

try:
    FrozenPoint(x=1, y=2, z=3)
except TypeError as err:
    print(err.args[0])

FrozenPoint.__slots__ = ("x", "y")


# ── Pattern Matching ──────────────────────────────────────────────────────────


@overload
def match_object(obj: int) -> str:
    ...
@overload
def match_object(obj: str) -> str:
    ...
@overload
def match_object(obj: complex) -> str:
    ...
@overload
def match_object(obj: float) -> str:
    ...
@overload
def match_object(obj: bytes) -> str:
    ...
@overload
def match_object(obj: bytearray) -> str:
    ...
def match_object(obj):
    if isinstance(obj, int):
        out = f"{obj} is an integer."
    elif isinstance(obj, str):
        out = f"String '{obj}' not empty."
    else:
        out = f"Ignoring unexpected object of type {type(obj).__name__}"
    return out


match_object(42)
match_object('hello')
match_object((1+1j))
match_object(float(42))
match_object(b'bytes')
match_object(bytearray([97