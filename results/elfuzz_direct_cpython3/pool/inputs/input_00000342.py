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
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(**{**data, "priority": Priority(data["priority"]), "status": Status(data["status"])})


# ── Slots ─────────────────────────────────────────────────────────────────────

class ExampleClass:
    __slots__ = ["_value"]

    def __init__(self):
        self._value = ""

    def set_value(self, value: str) -> None:
        self._value = value

    def get_value(self) -> str:
        return self._value


# ── Structural pattern matching ───────────────────────────────────────────────

def match_obj(obj: V) -> K:
    match obj:
        case str():
            return obj.upper()

        case list() as items:
            return items[-1].upper()

        case _: raise ValueError(f"Unexpected value: {obj!r}")

    # unreachable code
    assert False, "Unreachable"


def match_list(lst: list[V]) -> K:
    match lst:
        case []:
            return []

        case [first, second]:
            return first + second

        case [head] | [head, tail] | [*rest]:
            return head

        case [] | [_]: raise ValueError("Expected at least one item")

    # unreachable code
    assert False, "Unreachable"

# ── Walrus operator ───────────────────────────────────────────────────────────

def foo(x: int, y: int, z: int) -> int:
    match (x := x + 1), (y := y * 3), (z := z // 4):
        case (a, b, c) if a > b and b < c:
            return a
        case otherwise:
            return sum(otherwise)

assert foo(1, 2, 3) == 6
assert foo(-1, 2, 3) == 9
assert foo(1, -2, 3) == 7
assert foo(1, 2, -3) == 3
assert foo(-1, -2, -3) == -4


# ── Generics ──────────────────────────────────────────────────────────────────

# https://docs.python.org/3/library/asyncio-task.html#simple-example-of-async-await


# ── Exception groups ──────────────────────────────────────────────────────────

try:
    raise ExceptionGroup(
        title="Multiple exceptions",
        exceptions=[Exception(), ZeroDivisionError()],
    )
except ExceptionGroup as e_group:
    print(e_group.exceptions)

print(ExceptionGroup(title="Test").exceptions)


# ── __main__
# import inspect
# print(inspect.signature(match_list))