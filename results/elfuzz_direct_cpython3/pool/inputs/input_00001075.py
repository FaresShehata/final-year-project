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

# ── Classes and Interfaces ───────────────────────────────────────────────────


@runtime_checkable
class HasStatus(Protocol[K]):
    status: Status

@dataclasses.dataclass(order=True, frozen=True)
class Completed(K):     # K is HasStatus
    value: V
    timestamp: float = dataclasses.field(default_factory=time.time)
    status: Status = Status.SUCCESS

@dataclasses.dataclass(order=False, frozen=True)
class Pending(K):       # K has no order
    created_at: float = dataclasses.field(default_factory=time.time)
    status: Status = Status.PENDING


@dataclasses.dataclass(order=True, frozen=True)
class Running(Pending[V]):      # K has no order
    result: T | None             # K is has_order as well as has_status
    progress: float              # how much done? 0 <= x < 1

@dataclasses.dataclass(order=True, frozen=True)
class Failed(Running[V]):       # K has no order
    exn: BaseException


class Queue(Generic[K], list[K]):

    def append(self, obj: K) -> None:
        bisect.insort(self, obj)

    @overload
    def pop_first(self) -> K: ...
    @overload
    def pop_first(self, default: K) -> K | None: ...

    def pop_first(self, default: K | None = None) -> K | None:
        try:
            return self.pop(0)
        except IndexError:
            return default


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    address: Address

@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str

# ── Functions ────────────────────────────────────────────────────────────────


def get_person_by_lastname(input: dict[str, set[Person]]) -> dict[int, list[Person]]:
    """ Convert a dictionary of people by their last names to one with them by their ids """

    output : dict[int, list[Person]] = {}
    for lastname in input:
        for person in input[lastname]:
            if person.id not in output:
                output[person.id] = []
            output[person.id].append(person)

    return output


def run_task(task_id: int, task_fn: Callable[[int], Awaitable[T]], *args: T.args, **kwargs: T.kwargs) \
                      -> Completed[T]:
    """ Run an asynchronous function, record it's completion """

    future = asyncio.ensure_future(task_fn(task_id))
    completed = Completed(value=await future)
    return completed


async def await_all(tasks: list[Awaitable[T]]) -> list[Completed[T]]:
    """" Wait on all tasks """
    results = await asyncio.gather(*tasks)
    return [Completed(t) for t in results]


def map_to_completed(results: list[Awaitable[T]]) -> list[Completed[T]]:
    """ Map the results from all the tasks into completed instances """
    return [Completed(r) for r in results]


def filter_pending(results: list[Completed[V]]) -> list[Completed[V]]:
    """ Filter out pending tasks """

    # filter() doesn't work here because we are comparing completed vs. pending.
    # If we used it here, then for each item, we'd have to check both fields at once,
    # which is slower than just using a generator expression (which will do the filtering behind the scenes).
    #
    # So instead, we use a list comprehension.

    return [r for r in results if r.status == Status.RUNNING]

def filter_running(results: list[Completed[V]]) -> list[Completed[V]]:
    """ Filter out completed tasks """

    # filter() doesn't work here because we are comparing completed vs. running.
    # If we