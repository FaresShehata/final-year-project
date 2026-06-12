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
      >>> run_coroutines(foo()) == ('a', 'b')
    """
    tasks = [asyncio.create_task(coro) for coro in coros]
    results = []
    while len(results) < len(tasks):
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            results.append(task.result())
    return tuple(results)


async def run_until_complete(
    coro: Awaitable[T],
    *,
    timeout: float | None = None,
    quiet_failures: bool = False,
) -> tuple[T, None] | tuple[T, Exception]:
    if timeout is not None:
        coro = asyncio.wait_for(coro, timeout)
    try:
        result = await coro
        return result, None
    except Exception as exc:
        if quiet_failures:
            return None, None
        raise


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclasses.dataclass(order=True, unsafe_hash=True)
class Person:
    name: str
    age: int | None = None


@dataclasses.dataclass
class Animal:
    species: str
    weight: float | None = None
    height: float | None = None
    sex: str | None = None
    fur_color: str | None = None
    eyes: int | None = None
    tail_length: float | None = None


@dataclasses.dataclass
class Rectangle(Generic[V]):
    x: V
    y: V
    width: V
    height: V

    @property
    def area(self) -> V:
        return (self.width * self.height)

    @property
    def perimeter(self) -> V:
        return (self.width + self.height) * 2

    @classmethod
    def from_dict(cls, dct: dict[str, V]) -> Rectangle[V]:
        return cls(**dct)


Rectangle[int] = Rectangle[float]


# ── Slots ─────────────────────────────────────────────────────────────────────

class BaseClassSlots:
    pass

BaseClassSlots.__slots__ = ("x", "y")


class DerivedClassSlots(BaseClassSlots):
    def __init__(self, x: int, y: int, z: int) -> None:
        super().__init