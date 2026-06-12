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


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    pages: int
    rating: float

    def format_pages(self) -> str:
        if self.pages < 1000:
            return f"{self.pages}p"
        else:
            return f"{self.pages // 1000}k"


# ─── Generics ────────────────────────────────────────────────────────────────

_T = TypeVar("_T")


def find_max(values: list[_T], key: Callable[[_T], V] = lambda v: v) -> _T:
    max_value: _T | None = None
    for value in values:
        if max_value is None or key(max_value) < key(value):
            max_value = value
    return max_value


# ─────────────────────────────────────────────────────────────────────────────


async def main() -> None:

    print("┌────────────────────────────────────────────────────────────────────┐")
    print("│ Seed 02 - async/await, Protocols, dataclasses, __slots__,           │")
    print("│ structural pattern matching, walrus operator, typing generics,      │")
    print("│ exception groups, ExceptionGroup                                   │")
    print("└────────────────────────────────────────────────────────────────────┘\n")

    await test_async_await()
    await test_protocols()
    await test_data_classes()
    await test_generics()

    print("\n\n---------------------------------------------------------------\n\n")


# ── Async Await ──────────────────────────────────────────────────────────────

print("\n\n\t\t ┌─────────────────────────────────────────────┐ \n")


@overload
async def wait_for(
    coro_or_future: Coroutine[Any, Any, T],
    timeout: Any = ...,
    *,
    loop: Optional[AbstractEventLoop] = ...,
    check: Optional[Callable[[Any], bool]] = ...,
    count: int = ...,
    return_when: Literal["FIRST_COMPLETED"] = ...,
) -> T: ...


@overload
async def wait_for(
    coro_or_future: Future[T],
    timeout: Any = ...,
    *,
    loop: Optional[AbstractEventLoop] = ...,
    check: Optional[Callable[[Any], bool]] = ...,
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
    def from_dict(cls, d: dict[str, any]) -> T: ...


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    pages: int
    rating: float

    def format_pages(self) -> str:
        if self.pages < 1000:
            return f"{self.pages}p"
        else:
            return f"{self.pages // 1000}k"


@dataclasses.dataclass(slots=True)
class Point:
    x: int
    y: int
    z: int = 0


# ─── Generics ────────────────────────────────────────────────────────────────

_T = TypeVar("_T")


def find_max(values: list[_T], key: Callable[[_T], V] = lambda v: v) -> _T:
    max_value: _T | None = None
    for value in values:
        if max_value is None or key(max_value) < key(value):
            max_value = value
    return max_value


# ─────────────────────────────────────────────────────────────────────────────


async def main() -> None:

    print("┌────────────────────────────────────────────────────────────────────┐")
    print("│ Seed 02 - async/await, Protocols, dataclasses, __slots__,           │")
    print("│ structural pattern matching, walrus operator, typing generics,      │")
    print("│ exception groups, ExceptionGroup                                   │")
    print("└────────────────────────────────────────────────────────────────────┘\n")

    await test_async_await()
    await test_protocols()
    await test_data_classes()
    await test_generics()

    print("\n\n---------------------------------------------------------------\n\n")


# ── Async Await ──────────────────────────────────────────────────────────────

print("\n\n\t\t ┌─────────────────────────────────────────────┐ \n")


@overload
async def wait_for(
    coro_or_future: Coroutine[Any, Any, T],
    timeout: Any = ...,
    *,
    loop: Optional[AbstractEventLoop] = ...,
    check: Optional[Callable[[Any], bool]] = ...,
    count: int = ...,
    return_when: Literal["FIRST_COMPLETED"] = ...,
) -> T: ...


@overload
async def wait_for(
    coro_or_future: Future[T],
    timeout: Any = ...,
    *,
    loop: Optional[AbstractEventLoop] = ...,
    check: Optional[Callable[[Any], bool]] = ...,
    count: int = ...,
    return_when: Literal["ALL_COMPLETED"],
) -> Tuple[Future[T], ...]: ...


async def wait_for(coro_or_future: Union[Coroutine[Any, Any, T], Future[T]], *args: Any) -> Any:
    loop = get_running_loop()
    future = Future(loop=loop)
    task = Task(coro_or_future=future, loop=loop)
    try:
        return await loop.run_in_executor(None, task._waiter)
    finally:
        task.cancel()


