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


def test_sortedlist() -> None:
    l = SortedList[int]()
    for i in range(3):
        l.add(i * 4)
    assert [i for i in l] == [0, 4, 8]


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Foo:
    bar: int


foo = Foo(bar=7)
print(repr(foo))


# ── Structural Pattern Matching ────────────────────────────────────────────────

def match_list(l: list[V]) -> V:
    match l:
        case []:
            return "empty"
        case [_]:
            return "singleton"
        case [x, *_]:
            return f"{x} followed by {_}"

for s in ["empty", "singleton", "1 followed by 2"]:
    print(match_list([s]))


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def calc(n: int) -> int:
    await asyncio.sleep(random.random())
    return n * 2


# this works fine
@overload
def ensure(a: int) -> int:
    ...


# but not so well with the walrus operator...
@overload
def ensure(a: str) -> int:
    ...


def ensure(a: int | str) -> int:
    return a


async def main() -> None:
    start = time.monotonic()

    coros = [
        asyncio.create_task(calc(x))
        for x in range(20)
    ]

    results = await asyncio.gather(*coros)

    end = time.monotonic()
    print(f"{end-start:.2f}s")

    for r in results:
        await ensure(r)


asyncio.run(main())


# ── Typing Generics ───────────────────────────────────────────────────────────

def identity(x: T) -> T:
    return x

identity(tuple())  # OK
identity(list())  # Error!

def identity2(t: TypeVar('Type')) -> TypeVar('Type'):
    return t

identity2(str)("Hello")


# ── Exception Groups ───────────────────────────────────────────────────────────

try:
    raise KeyboardInterrupt
except BaseException as e:
    exc_group = ExceptionGroup("grouped exceptions",