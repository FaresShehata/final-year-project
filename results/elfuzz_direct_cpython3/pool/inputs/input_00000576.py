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
    status: Status = Status.PENDING
    completed_at: float | None = None

    @property
    def running_time(self) -> float | None:
        if self.status.is_terminal():
            return time.time() - self.completed_at
        else:
            return None

    def update_status(self, new_status: Status) -> None:
        self.status = new_status
        self.completed_at = time.time()


def get_task(id: int) -> Task | None:
    return TASKS.get(id)


TASKS: dict[int, Task] = {}


async def complete_tasks() -> None:
    for task_id, task in list(TASKS.items()):
        if not task.running_time and task.status == Status.RUNNING:
            task.update_status(Status.SUCCESS)
            print(f"task {task.id} finished successfully")


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotDataClass:
    """This class has no special storage characteristics"""


@dataclasses.dataclass(slots=True)
class WithInitSlotDataClass:
    """This class has only slots with non-default values"""


@dataclasses.dataclass(slots=True)
class WithInitAndDefaultSlotDataClass:
    a: int = 1
    b: int = 2


# ── Structural Pattern Matching ────────────────────────────────────────────────

def match_number(number: int | float) -> str:
    match number:
        case 0:
            return "zero"
        case _ as n if isinstance(n, int) or isinstance(n, float):
            return f"{n:.3f}"
        case _:
            raise ValueError(f"Invalid value: {number}")


def match_list(list_: list[str]) -> str:
    match list_:
        case []:
            return "empty list"
        case [a]:
            return f"one element: {a}"
        case [a, b]:
            return f"two elements: {a}, {b}"
        case _:
            return "lots of elements"


def match_tuple(tuple_: tuple[float, ...]) -> str:
    match tuple_:
        case ():
            return "empty tuple"
        case (x):
            return f"a single argument: {x}"
        case (_ as x, *rest):
            return f"{len(rest)} arguments: {x}, {' '.join(map(str, rest))}"

match_list