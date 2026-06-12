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

    while True:
        num_pending = len(pending_tasks)
        for idx, task in reversed(sorted(tasks)):
            if task.is_terminal():
                continue
            elif not task.status.is_terminal():
                task.transition(Status.RUNNING)
                task.tags.extend(["in-progress"])
                task.metadata["start"] = time.time()
                try:
                    result = await asyncio.wait_for(
                        task_runner(task), timeout=random.uniform(0.2, 1.9) * 10
                    )
                    print(result)
                except RuntimeError as e:
                    task.transition(Status.FAILED)
                    task.tags.extend(["error"])
                    task.metadata.update({"end": time.time(), "error": e})
                else:
                    task.transition(Status.SUCCESS)
                    task.tags.extend(["completed"])
                    task.metadata.update({"end": time.time()})
                finally:
                    task.tags.remove("in-progress")
                del tasks[idx]
                break
            elif idx < num_pending and pending_tasks[-1][0] == idx:
                _, task_in_progress = heapq.heappop(pending_tasks)
                print(f"{task.name}: skipped ({len(pending_tasks)} more)")
                task.transition(Status.CANCELLED)
                task_in_progress.tags.extend(["skipped"])
                task_in_progress.metadata.update({
                    "status": task.status.value,
                    "reason": f"Skipped because {task.name}"
                })
                task_in_progress.metadata.pop("start")
                task_in_progress.metadata.pop("end")
                tasks.append(task_in_progress)

        if not tasks and not pending_tasks:
            break

        num_pending = len(pending_tasks)
        print("Pending Tasks:")
        for idx, task in sorted(pending_tasks):
            if idx >=