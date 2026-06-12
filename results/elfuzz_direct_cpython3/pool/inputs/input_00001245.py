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
    x: int
    y: int

    def distance_to_origin(self) -> float:
        x, y = self.x, self.y
        return (x ** 2 + y ** 2) ** 0.5

    def mid_point(self, other: Point) -> Point:
        x = (self.x + other.x) / 2
        y = (self.y + other.y) / 2
        return Point(x, y)


@dataclasses.dataclass(frozen=True, order=True, slots=True)
class Circle(Point):
    radius: int

    def area(self) -> float:
        return math.pi * (self.radius ** 2)


@dataclasses.dataclass(slots=True)
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height


@dataclasses.dataclass(order=True)
class TimePoint(dataclasses.OrderedDict):
    time: float
    point: Tuple[float]

    def __getitem__(self, item: Tuple[float]) -> float:
        for key, value in self.items():
            if key == item:
                return value


# ── Slots ────────────────────────────────────────────────────────────────────

class SlotParent:
    name: str = "parent"
    age: int = 39

class SlotChild(SlotParent):
    name: str = "child"


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_point(point: Point) -> None:
    match point:
        case Point(0, 0):
            print("Origin")
        case Point(x=0, _):
            print("Y axis passing through", x)
        case Point(_, y=0):
            print("X axis passing through", y)
        case Point(_ as x, _ as y):
            print("Random point", x, y)
        case _:
            raise NotImplementedError


def match_list(items: list[dict[str, str]]) -> None:
    match items:
        case [item]:
            print(item["name"], item["age"])
        case [] | [_] if len(items) > 42:
            print("List has more than 42 elements")
        case [first, second, *_]:
            print(first, second)
        case []:
            print("Empty List!")
        case _:
            raise NotImplementedError


def match_tuple(t: tuple[int, ...], size: int = -1) -> None:
    match t:
        case () if size != -1:
            raise ValueError("Not enough values")
        case (a,) if a % 2 == 0 and size >= 0:
            print(a, f"{size} even numbers before")
        case (a, b) if a < 0 and b > 0:
            print(a, b, "are both positive")
        case (_, _) as t if len(t) <= 6:
            print(*t, len(t))
        case (_ as first, second, *rest) if sum(rest) > 8:
            print(first, second, rest, sum(rest))
        case []:
            print("empty!")
        case _:
            raise NotImplementedError


# ── Generics ───────────────────────────────────────────────────────────────────

_T = TypeVar("_T")


def get_first_odd_number(numbers: Iterable[_T]) -> _T:
    odd_numbers = filter(lambda n: isinstance(n, int) and n % 2 != 0, numbers)
    return next(iter(odd_numbers))


def get_all_even_numbers(numbers: Iterable[_T]) -> list[_T]: ...
    return []


def get_average_age(students: list[Student]):
    total_age = sum(student.age for student in students)
    average = total_age / len(students)
    return round(average, 2)


def get_product_of_multiples(numbers: list[int]) -> int | None:
    product = reduce(lambda acc, num: acc * num, numbers, 1)
    return product if any(num > 1e7 for num in numbers) else None


# ── Exception Groups ───────────────────────────────────────────────────────────

def example_exception_group() -> None:
    try:
        with open("/path/to/file.txt") as file:
            content = file.read# ── Walrus Operator ───────────────────────────────────────────────────────────

def example_walrus() -> None:
    some_dict = {"key": "value"}
    key_exists = True if "key" in some_dict else False
    print(key_exists)  # Output: True

    key_exists = "key" in some_dict or False
    print(key_exists)  # Output: