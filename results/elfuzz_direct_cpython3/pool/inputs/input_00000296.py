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
            priority=Priority[data["priority"]],
            status=Status(data["status"]),
            tags=data.get("tags", []),
        )


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotClass:
    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        cls.__dict__["_slot_fields"] = set(field for field in cls.__annotations__.keys() if isinstance(field, slot))


# ── Structural Pattern Matching ────────────────────────────────────────────────

def get_task(task_id: int) -> Task:
    tasks = {task.id: task for task in TASKS}
    match tasks.get(task_id):
        case None:
            raise ValueError(f"Task with ID '{task_id}' not found.")
        case task as t:
            print(t.to_dict())


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def calc_square_root(n: int) -> float:
    square_root = n ** 0.5
    await asyncio.sleep(random.random())
    return square_root


async def main():
    nums = range(30)
    results = [calc_square_root(num) for num in nums]
    square_roots = [result async for result in results]

    assert all(map(lambda r: round(r, 2) == round(i ** 0.5, 2), square_roots))


# ── Generics ──────────────────────────────────────────────────────────────────

def sum_ints(numbers: list[int]) -> int:
    return sum(numbers)


def sum_floats(numbers: list[float]) -> float:
    return sum(numbers)


def sum_numbers(numbers: list[T]) -> T:
    return sum(numbers)


# ── Exception Groups ───────────────────────────────────────────────────────────

@overload
def handle_exception(exc: BaseException) -> Awaitable[None]: ...

@overload
def handle_exception(
    exc: BaseException,
    on_error: Callable[[BaseException], Awaitable[None]],
) -> Awaitable[None]: ...

@overload
def handle_exception(
    exc: BaseException,
    on_error: Callable[[BaseException], Awaitable[None]],
    on_success: Callable[[str], Awaitable[None]],
) -> Awaitable[