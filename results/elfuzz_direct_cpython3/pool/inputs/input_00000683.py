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

class MultiDict(Generic[K, V]):
    """Multi-valued dictionary."""

    def __init__(self):
        self.table: dict[K, set[V]] = {}

    def add_value(self, key: K, value: V) -> None:
        if key not in self.table:
            self.table[key] = set()
        self.table[key].add(value)

    def get_values(self, key: K) -> set[V]:
        try:
            return self.table[key]
        except KeyError:
            raise ValueError(f"{key} does not exist.")

    def all_keys(self) -> list[K]:
        return list(self.table.keys())

    def all_values(self) -> list[V]:
        values: set[V] = set()
        for key in self.table.values():
            values.update(key)
        return list(values)


def multi_dict_demo(multi_dict: MultiDict[int, str]) -> None:
    multi_dict.add_value(0, "a")
    multi_dict.add_value(0, "b")
    multi_dict.add_value(1, "c")
    multi_dict.add_value(2, "d")
    print(multi_dict.all_keys())
    print(multi_dict.all_values())


multi_dict_demo(MultiDict())



# ── Slots ─────────────────────────────────────────────────────────────────────

class Book:
    __slots__ = ("title", "author")

    def __init__(self, title: str, author: str) -> None:
        self.title = title
        self.author = author


book = Book("Python Programming", "Guido van Rossum")
print(book.__dict__)  # {'title': 'Python Programming', 'author': 'Guido van Rossum'}
print(book.__slots__)  # ('title', 'author')
del book.__slots__


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_book(book: Book) -> str:
    match book:
        case Book(title="The Hitchhiker's Guide to the Galaxy",
                 author="Douglas Adams"):
            return f"Book '{book.title}' by {book.author}"
        case Book(author="Stephen King"):
            return "King's scary books!"
        case _:
            return "Unknown book"


def match_task(task: Task) -> str:
    match task:
        case Task(id=1, name="task one"):
            return "One"
        case Task(name