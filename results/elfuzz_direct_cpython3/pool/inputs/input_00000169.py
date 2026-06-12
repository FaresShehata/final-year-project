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
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "_history": self._history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class Student:
    first_name: str
    last_name: str
    age: int = dataclasses.field(repr=False)
    gender: str = dataclasses.field(compare=False)


def student_slots() -> None:
    student = Student(first_name="Nicholas", last_name="Zuckerberg", age=34)
    print(student.first_name, getattr(student, "last_name"))


# ── Structural Pattern Matching ───────────────────────────────────────────────

@overload
def f(x: int) -> int: ...
@overload
def f(x: float) -> float: ...
@overload
def f(x: str) -> str: ...
def f(x):
    if isinstance(x, int):
        return x * 2
    elif isinstance(x, float):
        return x * 2.0
    else:
        raise NotImplementedError()


@overload
def g(x: int) -> int: ...
@overload
def g(x: float) -> float: ...
@overload
def g(x: str) -> str: ...
def g(x):
    match x:
        case int():
            return x * 2
        case float():
            return x * 2.0
        case _:
            raise NotImplementedError()


@overload
def h(x: int) -> int: ...
@overload
def h(x: float) -> float: ...
@overload
def h(x: str) -> str: ...
def h(x):
    match x:
        case int() as i:
            return i * 2
        case float() as f:
            return f * 2.0
        case _:
            raise NotImplementedError()


def