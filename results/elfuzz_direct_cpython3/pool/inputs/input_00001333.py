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
    SUCCESS   = "success"
    FAILURE   = "failure"

@runtime_checkable
class AsyncReactor(Protocol[T]):
    def schedule(self, task: T) -> T:
        """Schedules a new task for execution."""


async def event_loop(reactors: list[AsyncReactor]) -> None:
    while reactors:
        for reactor in reactors:
            try:
                for task in await reactor.schedule():
                    if isinstance(task, tuple):
                        yield task
                    else:
                        yield (task,)
            except Exception as exc:
                print(f"[{exc.__class__.__name__}] {repr(exc)}")


def main() -> None:
    async def _main() -> None:
        tasks = [random.randint(-1_000_000, 1_000_000) for _ in range(5)]
        reactor = Reactor()
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                tg.create_task(tg.async_create_task(reactor.schedule(task)))
        results = []
        for result in event_loop([reactor]):
            if not isinstance(result, tuple):
                result = (result, )
            results.extend(result)
        assert len(results) == len(tasks), f"{len(results=)}, {len(tasks=)}"
        assert all(
            isinstance(r, (int, float)) and r.is_integer() for r in results
        ), f"{results=}"
        assert sorted(results) == sorted(set(results)), f"{results=}"

        # TODO: test exceptions handling

    asyncio.run(_main())


# ─── Classes ─────────────────────────────────────────────────────────────────

class Reactor(Generic[K, V], AsyncReactor[V]):
    """
    Custom reactor class that schedules tasks asynchronously.

    Args:
        max_tasks (int, optional): The maximum number of pending tasks to be scheduled.
                                   Defaults to None. If set to None, there is no limit.
        priority_queue (bool, optional): Whether to use a priority queue for scheduling tasks.
                                         Defaults to True. If True, tasks are scheduled based on their priority.
                                         If False, tasks are scheduled randomly.
    """

    def __init__(
        self, *, max_tasks: int | None = None, priority_queue: bool = True
    ):
        """
        Initialize the custom reactor.

        Args:
            max_tasks (int, optional): The maximum number of pending