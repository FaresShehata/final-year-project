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
        self.container.clear()


# ── Generics with type variables ───────────────────────────────────────────────

def find_max_index(container: list[V], value: V) -> int:
    i = -1
    for j, item in enumerate(container):
        if value <= item:
            continue
        i = j
    return i


# ── Walrus operator ───────────────────────────────────────────────────────────

def count_words(text: str) -> tuple[int, ...]:
    word_counts: dict[str, int]
    words = text.split()

    counts = Counter(words)
    word_counts = tuple(counts[word] for word in words)

    return word_counts


def count_words_2(text: str) -> tuple[int, ...]:
    words = text.split()
    word_counts: dict[str, int] = {}  # mutable default argument!
    for word in words:
        word_counts[word] += 1

    return tuple(word_counts[word] for word in words)


# ── Exceptions ─────────────────────────────────────────────────────────────────

class MyException(Exception): ...


async def my_coroutine() -> None:
    raise MyException("my_exception")


async def main() -> None:
    try:
        await my_coroutine()
    except MyException as e:
        print(f"Caught {e}")

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()


# ── Exception Groups ───────────────────────────────────────────────────────────-

# Equivalent to a Python 3.10 Union here.
class Error(RuntimeError):
    pass


class AsyncError(ExceptionGroup):

    def get_group_explanation(self) -> str:
        return f"{len(self.exceptions)} errors occurred:\n\n"

    def group_for_each_exception(self, func: Callable[[Exception], Any]) -> AsyncError:
        return AsyncError(*(func(e) for e in self.exceptions))


# ── Structural Pattern Matching ───────────────────────────────────────────────

def compute_value(a: int, b: int, c: int) -> int:
    match [a, b, c]:
        case 0, 0, 0:
            return 0
        case 1, _, _:
            return 1
        case _, 1, _:
            return 2
        case _, _, 1:
            return 3
        case _, _, _:
            return