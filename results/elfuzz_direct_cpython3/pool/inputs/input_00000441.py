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
            priority=getattr(Priority, data["priority"]),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    sex: str = dataclasses.field(compare=False)


@dataclasses.dataclass(frozen=True)
class Point2D:
    x: float
    y: float

    def __add__(self, other: Point2D) -> Point2D:
        return Point2D(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        return Point2D(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: Point2D) -> Point2D:
        return Point2D(x=self.x * other.x, y=self.y * other.y)

    def __truediv__(self, other: Point2D) -> Point2D:
        return Point2D(x=self.x / other.x, y=self.y / other.y)

    def distance(self, other: Point2D) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ─── Slots ───────────────────────────────────────────────────────────────────

class Point3D(Point): ...

class Point4D(Point): ...


# ─── Structural Pattern Matching ──────────────────────────────────────────────

def get_grade(student: dict[str, int]) -> str:

    if student["score"] > 90 and student["grade"] == "A":
        return "A+"

    if student["score"] >= 80 and student["grade"] != "B":
        return "B+"

    if student["score"] < 80 and student["grade"] != "C":
        return "C+"

    if student["score"] <= 60 and student["grade"] != "F":
        return "F"

    return "None"


def get_grade_structural(student: dict[str, int]) -> str:

    match student["grade"]:
        case "A" if student["score"] > 90:
            return "A+"

        case "B" if student["score"] >= 80:
            return "B+"

        case "C" if student["score"] < 80:
            return "C+"

        case "F" if student["score"] <= 60:
            return "F"

        case _:
            return "None"


def get_grade_pattern(student: dict[str, int]) -> str:

    match student["grade"], student["score"]:
        case ("A",