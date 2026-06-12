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
            status=getattr(Status, data["status"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def as_json(self) -> str:
        d: dict = self.to_dict()

        if not isinstance(d["id"], int):
            raise TypeError(f"Expected int for 'id', got '{d['id']}'")

        return json.dumps(d)


def task_fsm(task: Task) -> Status:
    """Finite State Machine transitioning the task's state."""
    match task.status:
        case Status.PENDING:
            task.transition(Status.RUNNING)
            return task.status

        case Status.RUNNING:
            if random.random() < 0.05:
                task.transition(Status.FAILED)
                return task.status

            elif random.random() < 0.03:
                task.transition(Status.CANCELLED)
                return task.status

            else:
                task.transition(Status.SUCCESS)
                return task.status

        case Status.SUCCESS:
            return task.status

        case Status.CANCELLED:
            return task.status

        case Status.FAILED:

            if random.random() <= 0.67:
                task.transition(Status.CANCELLED)
                return task.status

            else:
                task.transition(Status.RUNNING)
                return task.status

        case _:
            raise ValueError(f"Unexpected task state: {task.status.name}")


async def task_runner(task: Task) -> None:
    print(f"[{time.strftime('%c')}] Running task #{task.id}: {task.name}")

    while True:
        await asyncio.sleep(random.randint(1, 5))
        task.transition(await task_fsm())

        if task.status == Status.SUCCESS:
            break

        elif task.status == Status.CANCELLED:
            break

    print(f"[{time.strftime('%c')}] Finished task #{task.id}: {task.name}")
    print(f"[{time.strftime('%c')}] History:\n\t{' '.join(map(str, task._history))}\n")


async def task_manager(tasks: list[Task]) -> None:
    tasks.sort(key=lambda t: t.sort_key, reverse=True)

    async with asyncio.TaskGroup() as tg:
        done_tasks: list[Task] = []

        while len(done_tasks) != len(tasks):
            active_tasks = [t for t in tasks if t.status.is_terminal()]

            if len(active_tasks) > 0