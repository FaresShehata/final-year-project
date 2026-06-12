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

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        yield from self._data

    def __len__(self) -> int:
        return len(self._data)


# ── Slots ───────────────────────────────────────────────────────────────────-

class Person:
    __slots__ = ("name", "_age")

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        raise AttributeError("cannot set age")


p = Person("John Doe", 34)


# ── Structural pattern matching ────────────────────────────────────────────────

def take_action(task: Task) -> None:
    match task:
        case Task(id=_, name="build", priority=priority, status=Status.RUNNING):
            print(f"Build started at {time.time()} with priority {priority}")
        case Task(id=_, status=Status.SUCCESS):
            print(f"{task.name} succeeded!")
        case Task(name="run"):
            print(f"No action needed for running!")
        case Task(_, _, _, Status.CANCELLED):
            print("Cancelled!")
        case Task(_, name):
            print(f"No action needed for {name}")
        case Task(_, name, priority, Status.FAILED | Status.CANCELLED):
            print(f"{name} failed or cancelled.")
        case Task(_, name, priority, Status.FAILED):
            print(f"{name} failed.")
        case Task(_, name, priority, Status.RUNNING):
            print(f"{name} is still running.")

take_action(Task(id=1, name="build"))
take_action(Task(id=2, name="deploy"))
take_action(Task(id=3, name="run"))
take_action(Task(id=4, name="test"))

match [1, 2], 3:
    case [a, b], c:
        assert a == 1 and b == 2 and c == 3
    case _:
        raise ValueError("No matches found.")


# ── Walrus operator ───────────────────────────────────────────────────────────

async def get_random_number() -> int:
    await asyncio.sleep(random.random())
    return random.randint(1, 10)


async def main() -> None:
    total = 0
    while True:
        num = await get