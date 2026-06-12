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

    def get_distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
    

PointList = list[Point]


@dataclasses.dataclass(frozen=True)
class LineSegment:
    point_a: Point
    point_b: Point

    @property
    def length(self) -> float:
        dx = self.point_a.x - self.point_b.x
        dy = self.point_a.y - self.point_b.y
        return (dx**2 + dy**2)**0.5
    
    def intersects(self, other: LineSegment) -> bool:
        return False


def create_point_list(n: int) -> PointList:
    return [Point(x=random.random(), y=random.random())
            for _ in range(n)]

# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    name: str
    age: int
    gender: str

    __slots__: ClassVar[list[str]] = ["age", "gender"]


p1: Person = Person(name="John Doe", age=30, gender="male")
print(p1.__dict__)       # {'name': 'John Doe'}
print(p1.age)            # 30
del p1.name              # AttributeError: can't delete attribute '__weakref__'
with open("person.json", mode="w+") as f: json.dump(dataclasses.asdict(p1), f)


# ── Structural Pattern Matching ───────────────────────────────────────────────

@overload
def is_person(obj: object) -> bool: ...
@overload
def is_person(obj: Person) -> bool: ...
def is_person(obj): return isinstance(obj, Person)

person = {"name": "Alice", "age": 28}
for key, value in person.items(): print(key, value)
match person:
    case {"name": n, "age": a} if is_person(person):
        print(f"Name: {n}, Age: {a}")
    case {"name": _, "age": _}:
        print("Key-value pairs with name and age found")
    case {}:
        print("No key-value pairs found")
    case _: raise ValueError("Invalid person dictionary")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def fetch(url: str) -> bytes:
    await asyncio.sleep(random.randint(0, 4))
    return b"data"


urls: list[str] = [
    "https://example.com",
    "https://google.com",
    "https://yahoo.com",
]

tasks = []
for url in urls:
    task = asyncio.create_task(fetch(url))
    tasks.append(task)
    match await task: 
        case bytes():
            print(f"Fetched data from {url}")

# ── Typing Generics ───────────────────────────────────────────────────────────

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._container: list[T] = []

    def push(self, item: T) -> None:
        self._container.append(item)

    def pop(self) -> T:
        return self._container.pop()

    def __repr__(self) -> str:
        return repr(self._container)



# ── Exception Groups ───────────────────────────────────────────────────────────

try:
    raise KeyboardInterrupt
except KeyboardInterrupt as e:
    try:
        raise RuntimeError("Something went wrong") from e
    except Exception as e:
        exc_group = ExceptionGroup(
            title="Multiple errors occurred during execution",
            causes=[e],
        )
        raise exc_group

for cause in exc_group.exceptions:
    do_something_with_exception(cause)