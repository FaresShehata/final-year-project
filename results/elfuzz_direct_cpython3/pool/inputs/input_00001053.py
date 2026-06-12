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


def get_circles(points: Iterable[Xyz]) -> Generator[Circle]:
    for point in points:
        yield Circle(Xyz(point.x, point.y, 0), 3)


for circle in get_circles((Point(x, y) for x, y in [(4, 4), (-3, 7)])):
    print(circle.area())


# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    __slots__ = ("name", "_age")

    def __init__(self, name: str, age: int) -> None:
        super().__setattr__("name", name)
        super().__setattr__("_age", age)

    def __repr__(self) -> str:
        return f"Person(name={self.name}, age={self.age})"

    def __getattribute__(self, name: str) -> Any:
        if name == "age":
            return super().__getattribute__("_age")
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "age":
            raise AttributeError("'Person' object attribute 'age' is read-only")
        else:
            return super().__setattr__(name, value)

try:
    p = Person("John Doe", 30)
except AttributeError as e:
    assert type(e).__name__ == "AttributeError"


class Book:

    def __init__(self, title: str, author: str) -> None:
        self.title = title
        self.author = author

    @property
    def info(self) -> str:
        return f"{self.title} by {self.author}"


b = Book("The Great Gatsby", "F. Scott Fitzgerald")
assert b.info == "The Great Gatsby by F. Scott Fitzgerald"
book_info = b.info
print(book_info)
del book_info
print(b.info)




# ── Structural Pattern Matching ───────────────────────────────────────────────

x = [1, 2]

match x:
    case []:
        print("Empty!")
    case [first, second, *_]:
        print(first)
        print(second)
    case [_, last]:
        print(last)
    case [a, b, c, d]:
        print(a)
        print(c)
    case _:
        print("Unknown!")


class Foo:
    pass


class Bar(Foo): ...
class Baz(Foo): ...

if spec is not None:
    module = importlib.util.module_from_spec(spec)
else:
    raise ValueError("Module not found.")

sys.meta_path.append(module.__spec__)

print(importlib.import_module('module_name'))

