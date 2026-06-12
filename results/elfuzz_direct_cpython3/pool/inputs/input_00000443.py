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
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)


if TYPE_CHECKING:
    ...


T = TypeVar("T")
U = TypeVar("U")


def test() -> None:
    assert True


test()


# ── Enums ─────────────────────────────────────────────────────────────────────

# ── Base classes ─────────────────────────────────────────────────────────────-

@dataclasses.dataclass(frozen=True)
class Task:
    """
    A task to be performed.
    """

    id: int
    name: str
    priority: Priority
    status: Status
    tags: List[str]


@enum.unique
class Priority(enum.Enum):
    """Priorities of tasks."""

    NORMAL = 0
    HIGH = 1


@enum.unique
class Status(enum.enum):
    """Statuses of tasks."""

    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


# ─── The class hierarchy for the todo list ───────────────────────────────────

# ─── Task ────────────────────────────────────────────────────────────────────

# ─── Task ────────────────────────────────────────────────────────────────────


# ─── TodoList ────────────────────────────────────────────────────────────────

# ─── Async Context Managers ───────────────────────────────────────────────────

# ─── AsyncContextManager Decorator ────────────────────────────────────────────


async def run_task(task_id: int) -> None:
    print(f"Running task {task_id}...")


async def main():
    # Create a list of tasks with different priorities and statuses
    tasks = [
        Task(id=1, name="Task 1", priority=Priority.NORMAL, status=Status.TODO, tags=["a"]),
        Task(id=2, name="Task 2", priority=Priority.HIGH, status=Status.IN_PROGRESS, tags=["b"]),
        Task(id=3, name="Task 3", priority=Priority.NORMAL, status=Status.DONE, tags=["c"]),
        Task(id=4, name="Task 4", priority=Priority.HIGH, status=Status.TODO, tags=["d"]),
        Task(id=5, name="Task 5", priority=Priority.NORMAL, status=Status.IN_PROGRESS, tags=["e"]),
        Task(id=6, name="Task 6", priority=Priority.HIGH, status=Status.DONE, tags=["f"]),
    ]

    await asyncio.gather(*[run_task(task.id) for task in tasks])


if __name__ == "__main__":
    asyncio.run(main())

# ─── Awaitables, Generators, Coroutines, Tasks ───────────────────────────────

# ─── Async Functions ─────────────────────────────────────────────────────────

# ─── Coroutine Function ───────────────────────────────────────────────────────
"""
A coroutine function is a function that can be paused and resumed during its execution. 
This means it can perform asynchronous operations without blocking the main thread.

To create an asynchronous function, you use the async keyword before the function definition. 
Inside the function body, you can use await expressions to pause the coroutine and wait for other