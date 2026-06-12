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
class AsyncIterable(Protocol[K], Iterable[K]):
    async def __aiter__(self) -> AsyncIterator[K]: ...


async def _next(iterable: AsyncIterable[K]) -> K:
    async for x in iterable:
        return x


async def next_or_none(iterable: AsyncIterable[K]) -> K | None:
    try:
        return await _next(iterable)
    except StopAsyncIteration:
        return None


async def first(iterable: AsyncIterable[K]) -> K:
    return await _next(iterable)


def run_coroutines(coros: list[Awaitable[T]]) -> tuple[tuple[None, T], ...]:
    """
    Run a number of coroutines concurrently, returning results as a tuple.

    Note that the order of returned values will match their completion order.
    The idea here is to be able to use `run_coroutines` with a generator or
    other lazy sequence, without having to worry about the order of its
    elements. For example:

      >>> async def foo():
      ...     yield 'a'
      ...     yield 'b'
      ...
      >>> run_coroutines(foo())
    ('a', 'b')
    """

    result: list[T] = []
    tasks = [asyncio.create_task(coro) for coro in coros]
    while tasks:
        done, pending = await asyncio.wait(tasks)
        for task in done:
            result.append(await task)
        tasks[:] = pending
    return tuple(result)


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class DownloadResult:
    url: str
    filename: str
    file_size: int


@dataclasses.dataclass(slots=True)
class FileDownloadRecord:
    start_time: float
    end_time: float
    duration_ms: float
    download_result: DownloadResult


@dataclasses.dataclass(order=True, frozen=True)
class Task:
    """"""

    id: int
    name: str
    priority: Priority
    status: Status
    tags: frozenset[str]


# ── Serialisation ─────────────────────────────────────────────────────────────

def serialise(task: Task) -> dict:
    return {
        "id": task.id,
        "name": task.name,
        "priority": task.priority.name,
        "status": task.status.value,
        "tags": task.tags,
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
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

