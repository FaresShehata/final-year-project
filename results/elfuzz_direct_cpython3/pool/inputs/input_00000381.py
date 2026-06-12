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
    url: str
    filename: str
    start_time: float
    end_time: float
    download_result: DownloadResult


# ── Slots ────────────────────────────────────────────────────────────────────

# class Wallet:
#     """Wallet keeps track of money."""
#
#     __slots__ = ["_balance"]  # notice the underscore on balance!
#
#     def __init__(self, amount: int) -> None:
#         self._balance = amount
#
#     @property
#     def balance(self) -> int:
#         return self._balance
#
#     def withdraw(self, amount: int) -> None:
#         if not self.has_enough_balance(amount):
#             msg = f"Not enough funds ({self.balance}) for withdrawal ({amount})"
#             raise RuntimeError(msg)
#         self._balance -= amount
#
#     def deposit(self, amount: int) -> None:
#         self._balance += amount
#
#     def has_enough_balance(self, amount: int) -> bool:
#         return self._balance >= amount



# ── Structural pattern matching ───────────────────────────────────────────────


def find_us_states(name: str) -> list[str]:
    matches = []
    for state_abbrv in STATES:
        if re.search(rf"\b{re.escape(state_abbrv)}\b", name, flags=re.I):
            matches.append(state_abbrv)
    return sorted(matches)


def replace_us_states(word: str) -> str:
    """
    Replace US states' abbreviations in word with full names.
    """
    for abbrv, full_name in STATES.items():
        word = re.sub(abbrv, full_name, word, flags=re.I)
    return word


US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
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
            "metadata": self.metadata,
            "_history": [h.value for h in self._history],
        }

    @classmethod
    def from_dict(
        cls, d: dict[str, T], *, default_priority: Priority = Priority.NORMAL
    ) -> Task:
        task_id = d["id"]
        task_name = d["name"]

        try:
            task_priority = getattr(Priority, d["priority"]).value
        except KeyError as e:
            raise ValueError(f"Invalid priority: {e}") from e

        task_tags = d.get("tags") or []
        task_metadata = d.get("metadata") or {}

        return cls(
            task_id,
            task_name,
            Priority(task_priority),
            Status(d["status"]),
            task_tags,
            task_metadata,
            default_priority=default_priority,
        )


@dataclasses.dataclass
class Person:
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float
    description: str = ""
    email_addresses: frozenset[str] = dataclasses.field(default_factory=frozenset)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self.first_name}, {self.age}, {self.gender}"

