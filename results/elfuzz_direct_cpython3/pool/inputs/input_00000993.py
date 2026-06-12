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
    x: int
    y: int

    def distance_to_origin(self) -> float:
        x, y = self.x, self.y
        return (x ** 2 + y ** 2) ** 0.5

    def mid_point(self, other: Point) -> Point:
        x = (self.x + other.x) / 2
        y = (self.y + other.y) / 2
        return Point(x, y)


@dataclasses.dataclass(frozen=True, order=True, slots=True)
class Circle(Point):
    radius: int

    def area(self) -> float:
        return math.pi * (self.radius ** 2)


@dataclasses.dataclass(slots=True)
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height


@dataclasses.dataclass(order=True)
class TimePoint(dataclasses.OrderedDict):
    time: float
    point: Tuple[float]

    def __getitem__(self, item: Tuple[float]) -> float:
        for key, value in self.items():
            if key == item:
                return value


# ── Slots ────────────────────────────────────────────────────────────────────

class SlotParent:
    name: str = "parent"
    age: int = 39

class SlotChild(SlotParent):
    name: str = "child"


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person):
    match person:
        case Student(name="Alice"):
            print("Hello Alice")
        case Teacher(name=name):
            print(f"Hi teacher, my name is {name}")
        case _ as unknown:
            print(f"I don't know who you are, but I'm sorry.")


match_person(Student(name="Alice"))
match_person(Teacher(name="Bob"))
match_person(Guest())


# ── Walrus Operator ──────────────────────────────────────────────────────────

nums = [4, 8, 15, 16, 23, 42]
evens = []
for num in nums:
    if num % 2 == 0:
        evens.append(num)
print(evens)

evens = [num for num in nums if num % 2 == 0]
print(evens)

evens = [num for num in nums if (num := num * 2)]
print(nums)
print(evens)


# ── Generics ─────────────────────────────────────────────────────────────────

T1 = TypeVar("T1")

class Queue(Generic[T]):
    def __init__(self, lst=None) -> None:
        self._queue = deque(lst or [])

    def enqueue(self, obj: T) -> None:
        self._queue.append(obj)

    def dequeue(self) -> T:
        return self._queue.popleft()


QInts = Queue[int]()

QInts.enqueue(1)
QInts.enqueue(2)


# ── Exception Groups ──────────────────────────────────────────────────────────

try:
    raise ValueError("Something went wrong.")
except Exception as e:
    raise ExceptionGroup("Multiple exceptions", [e])


# ── Structured logging ────────────────────────────────────────────────────────

async def main():
    try:
        await do_something_async()
    except RuntimeError as e:
        logger.error(
            "RuntimeError occurred",
            exc_info=e,
            extra={"request_id": request.id},
        )

async def do_something_async():
    try:
        await some_async_task()
    except RuntimeError as e:
        raise


# ── Async Generator ───────────────────────────────────────────────────────────

async def fibonacci_gen(n: int) -> Iterable[int]:
    yield 0
    if n > 0: yield 1