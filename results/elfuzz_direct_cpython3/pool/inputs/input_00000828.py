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

    @property
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def quadrant(self) -> int:
        if self.x > 0 and self.y >= 0:
            return 1
        elif self.x < 0 and self.y > 0:
            return 2
        elif self.x < 0 and self.y <= 0:
            return 3
        else:
            return 4

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclasses.dataclass(eq=True, order=True, frozen=False, slots=True)
class Rectangle:
    top_left: Point
    bottom_right: Point

    @property
    def width(self) -> float:
        return abs(self.top_left.x - self.bottom_right.x)

    @property
    def height(self) -> float:
        return abs(self.top_left.y - self.bottom_right.y)


@dataclasses.dataclass(frozen=True, slots=True)
class Employee:
    first_name: str
    last_name: str
    age: int
    salary:K = TypeVar("K")
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

    @property
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def quadrant(self) -> int:
        if self.x > 0 and self.y >= 0:
            return 1
        elif self.x < 0 and self.y > 0:
            return 2
        elif self.x < 0 and self.y <= 0:
            return 3
        else:
            return 4

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


@dataclasses.dataclass(eq=True, order=True, frozen=False, slots=True)
class Rectangle:
    top_left: Point
    bottom_right: Point

    @property
    def width(self) -> float:
        return abs(self.top_left.x - self.bottom_right.x)

    @property
    def height(self) -> float:
        return abs(self.top_left.y - self.bottom_right.y)


@dataclasses.dataclass(frozen=True, slots=True)
class Employee:
    first_name: str
    last_name: str
    age: int
    salary: float
    active: bool = True

    def get_fullname(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_active(self, value: bool) -> None:
        self.active = value

    @staticmethod
    def find_oldest(*employees: Employee) -> Employee:
        oldest_employee = max(employees, key=lambda emp: emp.age)
        return oldest_employee


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    sex: str


# ── Structural Pattern Matching ───────────────────────────────────────────────

def do_something(a: int, b: int, c: int) -> str:
    match a, b, c:
        case 1, 2, 3:
            return ""
        case 1, _:
            return ""
        case _:
            return ""

def add_numbers(**kwargs: int) -> int:
    match kwargs:
        case {a: 1, b: 2, c: 3}:
            return 6
        case {a: 1, b: _, c: _}:
