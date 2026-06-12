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
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data["status"]),
            tags=data.get("tags", []),
        )

    def as_json(self) -> dict:
        return {
            "task_id": str(self.id),
            "name": self.name,
            "priority": self.priority.name.lower(),
            "status": self.status.name.lower(),
            "tags": ", ".join(self.tags),
        }


def task_from_string(task_str: str) -> Task:
    """Parse string into a Task instance."""
    task_info = json.loads(task_str.replace("'", '"'))
    tags = [tag.strip() for tag in task_info.pop("tags").split(",")]
    return Task(**{**task_info, "tags": tags})


def task_to_string(task: Task) -> str:
    if not isinstance(task, Task):
        raise TypeError(f"Invalid type: expected Task but got {type(task).__name__}")

    return json.dumps({
        **vars(task),
        "tags": ", ".join(task.tags),
    })


def print_tasks(tasks: list[Task]) -> None:
    for task in tasks:
        print(task.as_json())


async def edit_task_history(task: Task, duration: float) -> None:
    async for i in range(int(duration)):
        await asyncio.sleep(1 / 4)
        if not task.is_terminal():
            task.transition(Status.RUNNING)


async def main() -> None:

    # ── Async and Await ────────────────────────────────────────────────────────
    
    async def async_func() -> str:
        await asyncio.sleep(random.random())
        return f"Hello, I'm async!"

    async def sync_func() -> str:
        time.sleep(random.random())
        return "Hello, I'm sync!"

    async def func_with_awrap(*args, **kwargs) -> str:
        return await asyncio.wrap_future(asyncio.ensure_future(sync_func()))

    # The following two functions are equivalent.
    result1 = asyncio.run(func_with_awrap())
    result2 = asyncio.run(asyncio.wrap_future(asyncio.ensure_future(sync_func())))

    assert result1 == result2

    # The equivalent of the above code with an async function inside another
    # async function.
    async def nested_async_func() -> str:
        return await async_func()

    async def nested_sync_func() -> str:
        return sync_func()

    async def async_func_inside_nested_async_func() -> str:
        return await nested_async_func()

