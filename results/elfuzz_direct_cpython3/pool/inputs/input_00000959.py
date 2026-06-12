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
    LOW      = -1  # low priority
    NORMAL   = 0   # normal (default) priority
    HIGH     = 1   # high priority


@runtime_checkable
class Repr(Protocol[K]):
    @property
    def repr(self: K) -> str: ...


# ─── Classes ────────────────────────────────────────────────────────────────

# partial class demo
class Partial(Generic[T]):
    def __init__(self, func: Callable[[T], T]) -> None:
        self.func = func
    
    def __call__(self, *args: T.args, **kwargs: T.kwargs) -> T:
        return self.func(*args, **kwargs)


@dataclasses.dataclass
class Person:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Point:
    x: float
    y: float


# ────── Functions ───────────────────────────────────────────────────────────
def identity(x: T) -> T:
    return x


async def sleep_async(seconds: float | int = 1.0) -> float:
    await asyncio.sleep(seconds)
    return seconds


# ─────── Asyncio ───────────────────────────────────────────────────────────-

async def main() -> None:
    print(await sleep_async())  # => 1.0


# ─── Custom Types ───────────────────────────────────────────────────────────

PersonType = tuple[str, int]  # type alias
PointLike = tuple[float, ...]


def read_person_data(path: str) -> list[PersonType]:
    with open(path) as f:
        return [json.loads(line) for line in f.readlines()]
    
def read_point_data(path: str) -> list[tuple[float, ...]]:
    with open(path) as f:
        return [tuple(json.loads(line)) for line in f.readlines()]



# ─── Higher Order Functions ──────────────────────────────────────────────────

def map_(func: Callable[[T], V], it: Iterable[T]) -> list[V]:
    return [func(i) for i in it]


def filter_(pred: Callable[[T], bool], it: Iterable[T]) -> list[T]:
    return [i for i in it if pred(i)]


def reduce_(f: Callable[[T, T], T], it: Iterable[T], initial: T) -> T:
    acc = initial
    for i in it:
        acc = f(acc, i)
    return acc





# ───────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(main())

    # test custom types
    persons: list[Person] = [
        Person(name="Alice", age=34),
        Person(name="Bob", age=65),
        Person(name="Charlie", age=79),
    ]
    points: list[Point] = [Point(1.2, 3.8), Point(-1.7, 1.9)]
    assert len(persons) == 3 and len(points) == 2

    # test higher order functions
    person_names: list[str] = map_(lambda p: p.name, persons)
    ages_sorted: list[int] = sorted(map_(lambda p: p.age, persons))
    names_filtered: list[str] = filter_(lambda n: n.startswith("B"), person_names)
    summed_ages: int = reduce_(lambda a, b: a + b, map_(lambda p: p.age, persons), 0)
    doubled_ages: list[int] = map_(lambda a: a * 2, ages_sorted)
    avg_age: float = reduce_(lambda a, b