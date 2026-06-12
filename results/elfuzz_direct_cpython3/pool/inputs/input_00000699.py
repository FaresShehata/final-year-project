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

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> Task: ...


def task_runner(task: Task) -> Task:
    print(f"Running task {task.id}:", end=" ")
    for t in range(random.randint(3, 8)):
        print(".", end="", flush=True)
        await asyncio.sleep(random.random() / 10)
    if random.choice([True, False]):
        raise RuntimeError("Oops!")
    task.transition(Status.SUCCESS)
    print("done")
    return task


async def main() -> None:
    tasks: list[Task] = [
        Task(id=i, name=f"Task-{i}") for i in range(7)
    ]
    pending_tasks: list[Tuple[int, Task]] = []
    while tasks or pending_tasks:

        # get next pending task
        for index, task in enumerate(pending_tasks):
            if task[1].status != Status.RUNNING:
                del pending_tasks[index]
                break
        else:
            task = tasks.pop(0)
            task.transition(Status.RUNNING)
            pending_tasks.append((len(tasks), task))
            task_id = task.id
            task_name = task.name
            task_priority = task.priority.value
            loop.create_task(
                task_runner(task),
                name=f"{task_name}_{task_id}",
            )
            continue

        # all pending tasks are running
        for _, task in pending_tasks:
            if task.status == Status.CANCELLED:
                pending_tasks.remove((len(pending_tasks)-1, task))
                break
        else:
            raise ValueError("All tasks are cancelled")
        
        # find the first completed task
        completed_task_index = pending_tasks[-1][0]
        for j in range(completed_task_index+1, len(pending_tasks)):
            if pending_tasks[j][1].status.is_terminal():
                completed_task_index = j

        # remove it from the pending list and switch it to Success state
        pending_task_to_cancel = pending_tasks.pop(completed_task_index)[1]
        pending_task_to_cancel.transition(Status.CANCELLED)
        for k in range(len(pending_tasks)):
            if pending_tasks[k][1].priority > pending_task_to_cancel.priority:
                pending_task_to_cancel.transition(Status.SUCCESS)
                pending_tasks.insert(k, (completed_task_index, pending_task_to_cancel))
                break
        


if __name__ == "__main__":
    asyncio.run(main())