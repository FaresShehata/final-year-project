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
            "id"      : self.id,
            "name"    : self.name,
            "priority": self.priority.value,
            "status"  : self.status.value,
            "tags"    : [tag.lower() for tag in self.tags],
            "metadata": self.metadata,
            "_history": [str(status).lower() for status in self._history],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        default_priority: Priority = Priority.NORMAL,
        default_tags: list[str] = [],
        default_metadata: dict = {},
    ) -> Task:
        tags = [
            tag.strip().lower()
            for tag in data.pop("tags") if tag and len(tag.split()) == 1
        ]

        return cls(
            id=data["id"],
            name=data.get("name"),
            priority=Priority(data["priority"] or default_priority),
            status=Status(int(data["status"].lower())),
            tags=tags or default_tags,
            metadata={**default_metadata, **data},
        )

@dataclasses.dataclass(slots=True)
class Greeting:
    message: str = "Hello"
    counter: int = 0

    def say_hello(self) -> str:
        self.counter += 1
        return f"{self.message} {self.counter}"


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# ── Structural Pattern Matching ─────────────────────────────────────────────—

class Cat:

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

cat_1 = Cat(name="Mia", age=3)
cat_2 = Cat(name="Garfield", age=7)

match cat_1:
    case Cat(name="Mia", age=3):
        print("Matched Mia!")
    case Cat(_, age=42):
        print("Matched a cat with the age of 42!")

match cat_2:
    case Cat(name, age=42):
        print(f"Mewo! {name}, I'm your uncle!")

ListLike = typing.Union[list, tuple]


def concat(*args: ListLike[T]) -> list[T]:
