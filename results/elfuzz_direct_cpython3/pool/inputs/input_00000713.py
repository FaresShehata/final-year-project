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


@dataclasses.dataclass(order=True)
class TimePoint(Point):
    z: float = 0.0

    def __post_init__(self) -> None:
        super().__setattr__("z", round(super().x + super().y + super().z))


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def get_random_int(count: int) -> list[int]:
    ints = []
    while count > 0:
        n = await random.randint(0, 1_000_000)
        ints.append(n)
        count -= 1
    return ints


async def main() -> None:
    start = time.time()
    ints = await get_random_int(100_000)
    end = time.time()

    print(f"Got {len(ints)} random integers in {end - start:.2f}s")
    print(max(ints))
    print(min(ints))
    print(sum(ints))

print(main())
start = time.perf_counter()


# ── Generics ───────────────────────────────────────────────────────────────────

def median(nums: list[float]) -> float:
    if len(nums) == 0:
        raise ValueError("empty list of numbers")
    nums.sort()
    middle_index = len(nums) // 2
    if len(nums) % 2 == 1:
        return nums[middle_index]
    else:
        return (nums[middle_index] + nums[middle_index + 1]) / 2


def remove_duplicates(items: Iterable[T]) -> set[T]:
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def groupby(
    groups: list[tuple[bool, ...]], predicate: Callable[[tuple[bool, ...]], T]
) -> dict[T, list[tuple[bool, ...]]]:
    result: dict[T, list[tuple[bool, ...]]] = {}
    for g in groups:
        key = predicate(g)
        if key not in result:
            result[key] = [g]
        else:
            result[key].append(g)
    return result


def flatten(*args: any) -> list[list[any]]:
    return sum(args, [])


def transpose(matrix: list[list[Any]]) -> list[list[Any]]:
    return [
        [row[i] for row in matrix]
        for i in range(len(matrix[0]))
    ]


# ── Structural Pattern Matching ────────────────────────────────────────────────

def eat_fruit(fruits: list[str], fruits_to_eat: list[str]) -> str:
    for fruit in fruits:
        match fruit:
            case "apple":
                continue
            case "pear":
                break
            case _:
                return f"I don't like eating a {fruit}"
    for fruit in fruits_to_eat:
        match fruit:
            case "banana":
                continue
            case "peach":
                break
            case _:
                return f"I'll eat that {fruit} later."
    return "I love eating apples and bananas!"


# ── Exception Groups ───────────────────────────────────────────────────────────

def divide(a: float, b: float) -> tuple[float, float]:
    try:
        return a /