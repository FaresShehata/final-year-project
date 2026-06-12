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
class Comparable(Protocol[T]):
    def compare_to(self, other: T) -> int: ...



# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Task:

    name: str
    status: Status = Status.PENDING
    priority: Priority = Priority.NORMAL
    dependencies: set[int] = dataclasses.field(default_factory=set)
    sort_key: float = dataclasses.field(init=False, hash=False, compare=False)

    def __post_init__(self):
        self.sort_key = random.random()

    def transition(self, new_status: Status):
        self.status = new_status

    def run(self):
        raise NotImplementedError()


@dataclasses.dataclass(order=True)
class TimerTask(Task):

    duration: float
    deadline: float = dataclasses.field(init=False, repr=False, default=None)

    def __post_init__(self):
        super().__post_init__()
        self.deadline = time.time() + self.duration

    def run(self):
        try:
            while True:
                if time.time() < self.deadline:
                    yield None
                else:
                    self.transition(Status.SUCCESS)
                    break
        except asyncio.CancelledError:
            self.transition(Status.CANCELLED)


@dataclasses.dataclass(order=True)
class WorkerThreadTask(Task):

    priority: Priority = dataclasses.field(compare=True)
    dependencies: set[int] = dataclasses.field(repr=False, default_factory=set)
    thread_id: int = dataclasses.field(init=False, repr=False, compare=False)

    def __post_init__(self):
        super().__post_init__()
        self.thread_id = threading.get_ident()

    def run(self):
        try:
            while True:
                if self.priority > Priority.HIGH:
                    yield None
                else:
                    self.transition(Status.SUCCESS)
                    break
        except asyncio.CancelledError:
            self.transition(Status.CANCELLED)


@dataclasses.dataclass(order=True)
class RandomWorkerThreadTask(WorkerThreadTask):

    def __post_init__(self):
        super().__post_init__()

    def run(self):
        try:
            while True:
                if random.random() < 0.5:
                    self.transition(Status.SUCCESS)
                    return
                else:
                    yield None
        except asyncio.CancelledError:
            self.transition(Status.CANCELLED)


@dataclasses.dataclass(order=True)
class AsyncioTimerTask(TimerTask):

    def __post_init__(self):
        super().__post_init__()
        num_pending = len(pending_tasks)
        for idx, task in reversed(sorted(tasks)):
            if task.is_terminal():
                continue
            elif not task.status.is_terminal():
                future = asyncio.ensure_future(
                    task.run(), loop=loop
                )
                task.transition(Status.RUNNING)
                pending_tasks.append((idx, task))
            else:
                task.transition(Status.SUCCEEDED)
                print(f"Succeeded: {task.name}")
        if num_pending == len(pending_tasks):
            break
        else:
            print(f"{len(pending_tasks)} tasks are running")

    await asyncio.wait([
        asyncio.create_task(task_runner(t)) for _, t in pending_tasks
    ])
    for t in sorted(tasks, key=lambda t: t.sort_key):
        print(t)


