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


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Address:
    street_number: str
    street_name: str
    city: str


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    last_name: str
    age: int
    address: Address
    friends: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    isbn: int
    rating: float = 0.0


# ── Slots ─────────────────────────────────────────────────────────────────────

Person.__slots__ = ("name", "last_name")


# ── Structural pattern matching ───────────────────────────────────────────────

def get_status(person: Person) -> str:
    match person:
        case Person(name="John"):
            return "John is here!"
        case Person(name="Jane") as jane:
            return f"{jane.age} years old."
        case _:
            return f"No information about {person.name}"


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def run_forever() -> None:
    while True:
        await asyncio.sleep(random.randint(1, 3))
        print("Hello world!")


# ── Typing Generics ───────────────────────────────────────────────────────────

class MyList(Generic[V]):

    def append(self, item: V) -> None:
        raise NotImplementedError()


# ── Exception Groups ───────────────────────────────────────────────────────────

try:
    raise ValueError("Something went wrong!")
except Exception as e:
    group = ExceptionGroup(
        "Exception Group",
        [e],
    )
    raise group


# ── Types ─────────────────────────────────────────────────────────────────────

def parse_json(json_data: str) -> list[dict[str, str]]:
    try:
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON data!") from e


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:

    loop = asyncio.get_event_loop()

    # task = loop.create_task(run_forever())
    # handle = loop.create_future()
    # future = asyncio.wait_for(handle, timeout=3)
    #        self._data: list[T] = []

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


# ── Async machinery ───────────────────────────────────────────────────────────

