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
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data["priority"]],
            status=Status(data["status"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True, order=True)
class FrozenPoint:
    x: float
    y: float

    def distance(self, other: FrozenPoint) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(x: T) -> T:
    match x:
        case None as n:
            raise ValueError(f"{n=} not allowed") from None
        case x if isinstance(x, str):
            print(f"'{x}' is a string")
        case x if isinstance(x, bool):
            print(f"x={x} is a boolean")
        case x if isinstance(x, (bool, int)):
            print(f"this one too... x={x}")
        case x if hasattr(x, "__dict__"):
            for attr_name in ["foo", "bar"]:
                try:
                    getattr(x, attr_name)
                except AttributeError:
                    continue
        case _:
            raise ValueError(f"I don't know how to handle this type: {type(x)}")


match(None)


# ── Walrus Operator ──────────────────────────────────────────────────────────

async def demo_walrus() -> None:
    async def foo() -> str:
        return await bar()

    async def bar() -> str:
        return f"Hello {'world'}!"

    zzz = await foo()
    print(zzz)


# ── Generics & Typing ────────────────────────────────────────────────────────

def make_dict_of_lists(*args: tuple[T, ...]) -> dict[T, list[T]]:
    result: dict[T, list[T]] = {}
    for arg in args:
        key, value = arg
        entry_list = result.setdefault(key, [])
        entry_list.append(value)
    return