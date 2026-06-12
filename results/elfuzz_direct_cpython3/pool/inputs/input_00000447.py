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
            tags=set(data.get("tags", [])),
        )


# ── Generics ──────────────────────────────────────────────────────────────────

# https://docs.python.org/3/library/typing.html#generics
@overload
def add(a: T, b: V) -> Literal[T]: ...
@overload
def add(a: V, b: T) -> Literal[V]: ...


def add(a: V, b: T) -> V | T:
    return a + b


class MyGeneric(Generic[K]):
    def __init__(self, value: K): ...
    def __repr__(self) -> str: ...
    def __add__(self, other: Any) -> Self: ...
    def __eq__(self, other: Any) -> bool: ...
    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...


# ── Exceptions ─────────────────────────────────────────────────────────────────

class MyException(Exception):
    pass

async def foo() -> None:
    raise MyException()


# ── Walrus Operator ───────────────────────────────────────────────────────────

# https://www.python.org/dev/peps/pep-0572/
is_null = lambda x: x is None or isinstance(x, type(None))


# ── Structural Pattern Matching ───────────────────────────────────────────────

is_even = lambda n: n % 2 == 0
match n:
    case 0:
        print(f"{n} is even")
    case 1:
        print(f"{n} is odd")
    case _ if is_even(n):
        print(f"even number: {n}")
    case _:
        print(f"unknown")


@overload
def match_(x: int) -> str: ...
@overload
def match_(x: tuple[int]) -> int: ...
@overload
def match_(x: str) -> tuple[int]: ...
def match_(x: Any) -> Any:
    match x:
        case int():
            return str(x)
        case (tuple()):
            return len(x)
        case str():
            return x.split(",")


# ──