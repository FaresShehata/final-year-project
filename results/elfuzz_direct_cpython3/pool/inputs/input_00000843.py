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

@dataclasses.dataclass(slots=True)
class Xyz:
    xyz: tuple[float, float, float]


@dataclasses.dataclass(frozen=True)
class Circle:
    center: Xyz
    radius: float

    def area(self) -> float:
        return math.pi * self.radius**2



# ── Iterators & Generators ────────────────────────────────────────────────────

def fib(n: int) -> Generator[int, None, None]:
    yield 0
    if n > 0:
        yield 1
    last: int = 0
    next: int = 1
    for _ in range(1, n):
        last, next = next, last + next
        yield next


async def fibonacci() -> AsyncGenerator[int, None]:
    yield 0
    if n := await loop.sock_recv(sock, 8):
        ix = int.from_bytes(n, byteorder="big")
        yield from fib(ix)


@overload
def log(x: int) -> None: ...
@overload
def log(x: float) -> None: ...
def log(x: float | int) -> None:
    print(math.log10(x))


@overload
def factorial(n: int) -> int: ...
@overload
def factorial(n: float) -> float: ...
def factorial(n: float | int) -> float | int:
    if not isinstance(n, int):
        return n * factorial(n-1)
    result: int = 1
    while n >= 1:
        result *= n
        n -= 1
    return result


def fibonacci() -> Iterator[tuple[int, int]]:
    a, b = 0, 1
    while True:
        yield a, b
        a, b = b, a+b


async def fibonacci() -> AsyncIterator[tuple[int, int]]:
    a, b = 0, 1
    while True:
        yield a, b
        a, b = b, a+b


async def main() -> None:
    async for value in fibonacci():
        print(value)


asyncio.run(main())


# ── Structural Pattern Matching ───────────────────────────────────────────────

# https://www.python.org/dev/peps/pep-0636/
def match(obj: V, cases: dict[V, T], default: T | None = ...) -> Awaitable[T]:
    ...


async def match_task(task: Task) -> Awaitable[str]:
    match task:
        case Task(id=some_id, name="spam"):
            return "spam found"
        case Task(name="eggs"):
            return "eggs found"
        case Task(status=some_status, tags=["spam"]):
            return "tag spam found"
        case Task(metadata={"extra": "value"}):
            return "metadata extra found"
        case Task(metadata={"extra": _, "bar": ...} as m):
            return f"{m['extra']} - bar found"
        case Task(priority=priority_value, id=id_value, name=name_value, tags=[*tags_value], **kwargs):
            return f"{priority_value}, {id_value}, {name_value}, {tags_value}"
        case Task(tags=[], **kwargs):
            return "empty tag"
        case Task(**kwargs):
            return "default        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """SortedList with O(logn) insertion and removal operations."""

    items: list[T]

    def __repr__(self) -> str:
        return f"SortedList({self.items})"

    def __getitem__(self, i: int) -> T:
        return self.items[i]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        yield from self.items

    def __reversed__(self) -> Iterator[T]:
        yield from reversed(self.items)

    def append(self, item: T) -> None:
        bisect.insort_left(self.items, item)

    def extend(self, iterable: Iterable[T]) -> None:
        for item in iterable:
            bisect.insort_left(self.items, item)

    def insert(self, index: int, item: T) -> None:
