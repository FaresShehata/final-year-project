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

    def get_distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
    

PointList = list[Point]


@dataclasses.dataclass(frozen=True)
class LineSegment:
    point_a: Point
    point_b: Point

    @property
    def length(self) -> float:
        dx = self.point_a.x - self.point_b.x
        dy = self.point_a.y - self.point_b.y
        return (dx**2 + dy**2)**0.5
    
    def intersects(self, other: LineSegment) -> bool:
        return False


def create_point_list(n: int) -> PointList:
    return [Point(x=random.random(), y=random.random())
            for _ in range(n)]


# ── Slots ────────────────────────────────────────────────────────────────────

class Person:
    __slots__ = ("firstname", "lastname", "age")

    def __init__(self, firstname: str, lastname: str, age: int) -> None:
        self.firstname = firstname
        self.lastname = lastname
        self.age = age

    
class Employee(Person):
    __slots__ = ("company", "position")

    def __init__(
                self, 
                firstname: str, 
                lastname: str, 
                age: int, 
                company: str, 
                position: str
                ) -> None:

        super().__init__(firstname, lastname, age)
        self.company = company
        self.position = position


person_slots = Person("John", "Doe", 43)
employee_slots = Employee(
                        "Jane", 
                        "Doe", 
                        69, 
                        "Apple Inc.", 
                        "CEO"
                        )

print(person_slots.__dict__)
print(employee_slots.__dict__)


# ── Structural Pattern Matching ──────────────────────────────────────────────

def sum_if_positive(a: int, b: int) -> int|None:
    if a > 0 and b > 0:
        return a + b
    else:
        return None

def sum_if_positive_structural_pattern_matching(
                                                a: int, 
                                                b: int
                                                ) -> int|None:
    
    match (a, b): 
        case (int(a), int(b)) if a > 0 and b > 0:
            return a + b
        case _: 
            return        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
