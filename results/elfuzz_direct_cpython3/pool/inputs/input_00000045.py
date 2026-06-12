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
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


class PriorityQueue(Generic[K, V]):
    """
    Uses a heap with tuple of negative value and key/value pair.

    This works for any keys that support the total ordering, e.g., ints or floats.
    """

    def __init__(self) -> None:
        self._heap: list[tuple[float, K, V]] = []
        self._key_func: Callable[[tuple[float, K, V]], float] = lambda _: 0

    def push(self, key: K, val: V, *, reverse: bool = False) -> None:
        """Puts an element into the queue."""
        if reverse:
            key = -key
        heappush(self._heap, (self._key_func((key, val)), key, val))
        # We have to use this trick because we're using the same function as key
        # in both cases: the first means it won't be used when popping the topmost
        # element; the second will simply convert our reversed keys back to their original forms

    def pop(self, *, reverse: bool = False) -> tuple[K, V]:
        """Removes and returns the highest-priority element."""
        if reverse:
            return heappop(self._heap)[::-1]
        return heappop(self._heap)


def test_structural_pattern_matching() -> None:
    class Animal(Protocol): ...  # no fields, just methods

    def eat(animal: Animal) -> None:
        animal.eat()

    class Cat:
        def eat(self) -> None: print("Meow!")

    cat = Cat()
    eat(cat)  # okay!
    eat("NotCat")  # error!


async def test_exception_groups() -> None:
    try:
        raise KeyboardInterrupt
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            raise exc
        else:
            raise RuntimeError from exc

    # The above code can also be written like this:
    try:
        raise KeyboardInterrupt
    except BaseException as exc:
        group = ExceptionGroup("root cause", [exc])
        if isinstance(group.exceptions[0], KeyboardInterrupt):
            raise group.exceptions[0]
        else:
            raise RuntimeError from group
