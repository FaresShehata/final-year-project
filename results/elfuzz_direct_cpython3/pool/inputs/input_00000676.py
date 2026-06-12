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
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            name=data["name"],
            priority=getattr(Priority, data.pop("priority")),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


@dataclasses.dataclass
class User:
    username: str
    email: str
    points: int = 0

    def __str__(self) -> str:
        return f"<User: {self.username} ({self.points})>"


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class DataPoint:
    point_id: int
    value: float

    def __add__(self, other: DataPoint) -> DataPoint:
        return DataPoint(point_id=self.point_id, value=self.value + other.value)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def print_version(version_str: str) -> None:
    match version_str.split("."):
        case [major, minor, patch], tag: ...
        case [_]: raise ValueError("invalid version format")  # type: ignore
        case _: raise ValueError("could not find major.minor.patch")


def print_version_2(version_str: str) -> None:
    if "." in version_str:
        parts = version_str.split(".", maxsplit=2)
        try:
            major, minor, patch = map(int, parts[:3])
        except ValueError as e:
            raise ValueError(f"invalid version '{version_str}'") from e
    else:
        raise ValueError(f"unknown version '{version_str}'")

    if tag := parts[3:]:
        tag = tag[0]
    else:
        tag = ""

    match (major, minor, patch), tag:
        case (_, _, _), _:
            pass  # type: ignore
        case (_): raise ValueError("invalid version format")  # type: ignore
        case _: raise ValueError("could not find major.minor.patch")


def print_version_3(version_str: str) -> None:
    match *version_str.split("."), tag := version_str.split(".")[-1]:
        case [major, minor, patch], tag: ...
        case [_]: raise ValueError("invalid version format")        yield 1
    last: int = 0
    next: int = 1
    while True:
        last, next = next, last + next
        yield next


ListLike = typing.Union[list, tuple]


def concat(*args: ListLike[T]) -> list[T]:
