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


@dataclasses.dataclass(order=True)
class TimePoint(Point):
    z: float = 0.0

    def __post_init__(self) -> None:
        super().__setattr__("z", round(super().x + super().y + super().z))


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def get_random_int(count: int) -> list[int]:
    ints = []
    while count > 0:
        n = await random.randint(0, 1_000_000)
        ints.append(n)
        count -= 1
    return ints


async def main() -> None:
    start = time.time()
    ints = await get_random_int(100_000)
    end = time.time()

    print(f"Got {len(ints)} random integers in {end - start:.2f}s")


asyncio.run(main())


# ── Generics ──────────────────────────────────────────────────────────────────

class Task(Generic[T], Serialisable):

    id_: int
    _name: str
    _result: T | None
    _status: Status

    __slots__ = ("id_", "_name", "_result", "_status")

    def __init__(self, id_: int, name: str) -> None:
        self.id_      = id_
        self._name    = name
        self._result  = None
        self._status  = Status.PENDING

    def __repr__(self) -> str:
        return f"<Task {self.id_}: '{self._name}' ({self.status.name})>"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def status(self) -> Status:
        return self._status

    @property
    def result(self) -> T | None:
        return self._result

    async def run(self) -> T:
        await asyncio.sleep(random.random())
        self._status = Status.SUCCESS
        self._result = self._name.upper()

        return self._result

    def to_dict(self) -> dict[str, T | Status]:
        return {
            "id_":       self.id_,
            "name":      self._name,
            "status":    self._status.value,
            **({None: **{"result": None}} if self._status.is_terminal else {}),
        }

    @classmethod
   assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(list[K]):
    """Keeps elements sorted using bisect."""

    def add(self, item: K) -> None:
        bisect.insort(self, item)  # type: ignore[arg-type]

    def discard(self, item: K) -> None:
        idx = bisect.bisect_left(self, item)  # type: ignore[arg-type]
        if idx < len(self) and self[idx] == item:
            self.pop(idx)


def test_sortedList() -> None:
    l = SortedList[float]()
    for i in range(3):
        l.add(i * 4.99999)
    assert [i for i in l] == [0.0, 4.99999, 8.99997]


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(obj: Any) -> None:
    match obj:
        case int(n):
            print(f"{n} is an integer")
        case float(n):
            print(f"{n} is a float")
