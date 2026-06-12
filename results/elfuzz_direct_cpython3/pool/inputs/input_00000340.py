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
class PointSlots:
    x: float
    y: float

    def distance(self, other: PointSlots) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ── Structural Pattern Matching ───────────────────────────────────────────────

# https://www.python.org/dev/peps/pep-0634/
# https://docs.python-async.org/en/latest/tutorial/patterns.html#structural-pattern-matching

def match_any(a: int, b: int, c: int) -> int:
    match a, b, c:
        case 1, 2, 3:
            return 1
        case _, _, 3:
            return 2
        case 1, 2, _:
            return 3
        case _:
            return 4


def match_tuple(t: tuple[int, ...]) -> int:
    match t:
        case (): return len(t)
        case (_,): return len(t) - 1
        case (x, *xs): return xs.count(x)


def match_list(l: list[int]) -> int:
    match l:
        case []: return 0
        case [h]: return h
        case [_, *ts]: return ts[-1]


def match_string(s: str) -> int:
    match s:
        case '': return len(s)
        case _: return len([c for c in s if c.isupper()])


def match_range(r: range) -> int:
    match r:
        case range(): return sum(range(-1))
        case range(start=0, stop=s, step=-1): return sum(range(1, s))
        case range(start=s, stop=None, step=-1): return sum(range(s, 0))
        case range(start=None, stop=s, step=1): return sum(range(0, s))
        case _:
            raise ValueError("Invalid range")


def match_enum(e: enum.Enum) -> str:
    match e:
        case enum.Enum(value="foo"): return "foo"
        case enum.Enum(value="bar"): return "bar"
        case enum.Enum(): return "other"


def match_structured_data(d: dict) -> int:
    match d:
        case {"a": "b"}: return 1
        case {"a": "b", "c": v}:def f(x: str) -> str: ...
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
