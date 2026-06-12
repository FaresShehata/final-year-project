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

    def distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5


@dataclasses.dataclass(order=True, frozen=True, slots=True)
class Circle(Point):
    radius: float

    @property
    def area(self) -> float:
        return 3.14 * self.radius ** 2


# ── Slots ─────────────────────────────────────────────────────────────────────

# class Point:
#     __slots__ = ["x", "y"]

#     def __init__(self, x: float, y: float) -> None:
#         self.x = x
#         self.y = y


# class Circle(Point):
#     def __init__(self, center: Point, radius: float) -> None:
#         super().__init__(center.x, center.y)
#         self.radius = radius


# circle = Circle(Point(0, 0), 7)


# ── Structural Pattern Matching ───────────────────────────────────────────────

@overload
def move(value: int) -> None: ...
@overload
def move(value: float) -> None: ...
@overload
def move(value: str) -> None: ...
def move(value: V) -> None:
    if isinstance(value, int):
        print(f"Value of type int: {value}")
    elif isinstance(value, float):
        print(f"Value of type float: {value}")
    else:
        print("Value was a string")


move(1)
move(1.0)
move("Hello World")


# ── Walrus Operator ───────────────────────────────────────────────────────────

points: list[Point] = [Circle(0, 0), Circle(1, 1)]

for point in points:
    if (d := point.distance_to_origin()) < 1:
        print(d)


# ── Typing Generics ───────────────────────────────────────────────────────────

class MyList(list[T]):
    def append(self, item: T) -> None: ...
    def extend(self, iterable: Iterable[T]) -> None: ...
    def insert(self, index: int, value: T) -> None: ...
    def remove(self, value: T) -> None: ...
    def pop(self, index: int = -1) -> T: ...
    def clear(self) -> None: ...


my