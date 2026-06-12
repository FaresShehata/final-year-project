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
    start_time: float = 0.0
    end_time: float = 0.0

    def __post_init__(self):
        if not isinstance(self.priority, Priority):
            raise ValueError(f"Invalid Priority: '{self.priority}'")


@dataclasses.dataclass(order=True, frozen=True, slots=True)
class TaskRunResult(Generic[T]):
    task_id: int
    result: T
    exc_info: tuple[Exception, BaseException, TracebackType] | None = None


# ── Collections ────────────────────────────────────────────────────────────────

def _random_int() -> int:
    return random.randint(-99_999, 99_999)


def _add_to_heap(heap: list[tuple[int, K]], item: K, key: Callable[[K], int]) -> None:
    bisect.insort_left(heap, (key(item), item))


async def _sleep_and_add(heap: list[tuple[int, K]], seconds: float) -> None:
    await asyncio.sleep(seconds)
    _add_to_heap(heap, _random_int(), lambda x: abs(x - _random_int()))


def _run_tasks(tasks: set[Task]) -> set[Task]:
    for task in tasks:
        task.status = Status.RUNNING
        task.start_time = time.time()

    return tasks


async def _wait_for_task(task: Task) -> None:
    while task.status.is_terminal():
        await asyncio.sleep(0.01)


async def _check_end_times_and_update_status(
    heap: list[tuple[int, K]],
    results: deque[TaskRunResult[K]],
    finished_tasks: set[Task],
) -> None:
    while len(results) > 0 and results[0].task_id == finished_tasks.pop().id:
        result = results.popleft()
        if result.exc_info:
            task = [t for t in finished_tasks if t.id == result.task_id][0]
            task.status = Status.FAILED
            task.end_time = time.time()
        else:
            task = [t for t in finished_tasks if t.id == result.task_id][0]
            task.status = Status.SUCCESS
            task.end_time = time.time()


async def _process_results(
    heap: list[tuple[int, K]],
    results: deque[TaskRunResult[K]],
    finished_tasks: set[