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
    age: int
    height: float = 178.34
    weight: float = 67.98

    def say_hi(self) -> str:
        return f"Hi, I'm {self.name}."


@dataclasses.dataclass(slots=True)
class Position:
    latitude: float
    longitude: float

    @property
    def distance_to(self, target_position: Position) -> float:
        # Calculate distance between two points on earth's surface given their
        # latitudes and longitudes using haversine formula.
        delta_latitude = (target_position.latitude - self.latitude) * (pi / 180)
        delta_longitude = (target_position.longitude - self.longitude) * (pi / 180)
        a = sin(delta_latitude / 2)**2 + cos(self.latitude * (pi / 180)) * \
            cos(target_position.latitude * (pi / 180)) * sin(delta_longitude / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        radius_of_earth_in_km = 6371
        km = c * radius_of_earth_in_km
        return km


@dataclasses.dataclass()  # default slots=False
class PositionWithSlots:
    latitude: float
    longitude: float


# ── Structural Pattern Matching ────────────────────────────────────────────────

def get_temperature(unit: str) -> float:
    units = {
        "celsius": 273.15,
        "fahrenheit": 32 + 9/5 * 273.15,
    }
    m = re.match(r"^([cf])(\d+)$", unit)
    assert m is not None
    key, value = m.groups()
    return units[key.lower()] + int(value)


def get_temperature_structural_pattern_matching(unit: str) -> float:
    match unit:
        case "celsuis":
            return 273.15
        case "fahrenheit":
            return 32 + 9/5 * 273.15
        case _:
            raise ValueError(f"Unknown unit '{unit}'")


# ── Walrus Operator ────────────────────────────────────────────────────────────

def sum_up(n: int) -> int:
    total = 0
    i = n //