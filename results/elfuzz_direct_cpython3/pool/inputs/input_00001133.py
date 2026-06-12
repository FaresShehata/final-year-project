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
    """SortedList with O(logn) insertion and removal operations."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def __getitem__(self, item: int) -> T:
        return self._items[item]

    def insert(self, i: int, val: T) -> None:
        bisect.insort_left(self._items, val, lo=i, hi=len(self))

    def append(self, val: T) -> None:
        bisect.insort_right(self._items, val)

    def pop(self, i: int = -1) -> T:
        return self._items.pop(i)


# ── Async generators ───────────────────────────────────────────────────────────

async def countdown(n: int) -> None:
    while n > 0:
        yield n
        await asyncio.sleep(0.5)
        n -= 1


async def countup(n: int) -> None:
    for i in range(n + 1):
        yield i
        await asyncio.sleep(0.5)


async def main(countdown_generator: Generator[int]) -> None:
    async for num in countdown_generator:
        print(num)
        if num == 4:
            break
    else:
        raise RuntimeError("oops")


async def wait_for_event(event: Event) -> None:
    while not event.is_set():
        await asyncio.sleep(0.1)


# ── Signals ───────────────────────────────────────────────────────────────────

Signal = asyncio.Event()

@Signal.connect
def on_signal() -> None:
    print(f"{time.asctime()} Signal received!")

print(Signal.is_set())  # False
Signal.set()
print(Signal.is_set())  # True
Signal.clear()
print(Signal.is_set())  # False

for signal in iter(Signal.wait, None):  # or use `wait` as the sentinel value
    print(time.asctime(), signal)

SIGNAL_LISTENER = Signal.listen()


# ── Walrus Operator ───────────────────────────────────────────────────────────

a = "hello"
b = "world!"

start = time.monotonic()
result = (a := "goodbye") + (b := "earth!")
duration = time.monotonic() - start

print(result, duration)

# ── Named Tuples ──────────────────────────────────────────────────────────────

# If `namedtuple` behaves like a regular class, `__repr__` returns something
# like "<NT.MyClass    return header + b"\x00" * (HEADER_SIZE - len(header))  # padding to align with 8-byte boundary


def unpack_header(buf: memoryview) -> tuple[int, int, bytes]:
    return struct.unpack(HEADER_FMT, buf[:HEADER_SIZE])


# ── Array packing ─────────────────────────────────────────────────────────────

def int_array(size: int, value: int) -> array.array:
    """Create an integer array with given size and content."""
    arr = array.array("i")             # signed 32-bit integers
    arr.extend([value] * size)
    return arr


def str_array(size: int, value: str) -> array.array:
    """Create a string array with given size and content."""
    arr = array.array('c', value.encode())
