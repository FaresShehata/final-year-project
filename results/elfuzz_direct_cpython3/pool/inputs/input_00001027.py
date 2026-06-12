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


# ── Data classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Item(Generic[K]):
    priority: int
    value: K

    # noinspection PyUnresolvedReferences
    def __repr__(self):
        return f"Item({self.priority=!r}, {self.value})"


@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    address: Address
    phone_numbers: tuple[str]
    email_address: str = dataclasses.field(default="none@example.com", compare=False)


@dataclasses.dataclass(frozen=True, slots=True)
class Address:
    street_name: str
    house_number: str | None = None


# ── Generic types ────────────────────────────────────────────────────────────

class Array[T]:
    def __init__(self, values: list[T] | None = None):
        if values is None:
            values = []
        self.values = values

    def append(self, item: T):
        self.values.append(item)

    def pop(self) -> T:
        return self.values.pop()

    def items(self) -> Iterator[T]:
        yield from self.values

    def count(self, item: T) -> int:
        return self.values.count(item)


class Factory[G]:
    def __init__(self):
        self.generation = 0

    def create(self) -> G:
        self.generation += 1
        return G(self.generation)


# ── Async/await ─────────────────────────────────────────────────────────────

async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def main() -> None:
    for _ in range(3):
        print(await get_random_number())
        await sleep(1.0)


async def get_random_number() -> float:
    return random.random()


asyncio.run(main())


# ── Protocols ───────────────────────────────────────────────────────────────

P = TypeVar("P")


@runtime_checkable
class Iterable(P):
    ...  # pragma: no cover

@runtime_checkable
class Container(P):
    ...


# ── Structural Pattern Matching ─────────────────────────────────────────────

def what_is(x: object) -> str:
    match x:
        case int():
            return "int"
        case float():
            return "float"
        case complex():
            return "complex number"
        case _:
            return "other type (or a subtype)"


print(what_is(4))
print(what_is(4.5))
print(what_is(complex(1, -2)))
print(what_is(None))


class Point(tuple[float, float]):
    @property
    def distance_to_origin(self) -> float:
        return sum([x ** 2 for x in self])

    def __str__(self) -> str:
        return super().__str__() + " at origin."


p = Point((3.0, 4.0))
print(p.distance_to_origin)
print(str(p))

x = p[0]

match p:
    case []:
        print("empty")
    case [Point(), *rest]:
        print("point, followed by", len(rest), "other points.")
    case [any_point, Point(), any_other_point]:
        print("a point followed by another point")

try:
    match p:
        case [Point()] as single_pt:
            print(single_pt)
except TypeError as e:
    print(e)


# ── Walrus Operator ─────────────────────────────────────────────────────────

nums = [random.randint(0, 9) for _ in range(8)]

sum_of_squares = sum(n*n for n in nums)

largest_num = max(nums, key=lambda num: num**2)
smallest_num = min(nums, key=lambda num: num**2)

index = next(i for i, num in enumerate(nums) if num == largest_num or num == smallest_num)

min_val = min(num**2 for num in nums)

count = sum(len(str(num)) % 2 == 0 for num in nums)

total_sum = sum(nums[i] for i in range(len(nums)) if not i % 2)

num_with_max_digits = max(nums, key=lambda num: len(str(num)))

max_nums = sorted(nums, key=lambda num: len(str(num)), reverse=True)[:3]


# ── Typing Generics ──────────────────────────────────────────────────────────

ArrayInt = Array[int]

factory = Factory[Any]
g = factory.create