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

# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    name: str
    age: int
    gender: str

    __slots__: ClassVar[list[str]] = ["age", "gender"]


p1: Person = Person(name="John Doe", age=30, gender="male")
p2: Person = Person(name="Jane Doe", age=28, gender="female")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def greet_person(person: dict[str, str]) -> None:
    match person.values():
        case ["Alice", _]:
            print("Hello Alice!")
        case ["Bob", "b"]:
            print("Hello Bob!")
        case ("Charlie", *names):
            if names:
                print(f"Hello {', '.join(names)}!")
            else:
                print("Hello Charlie!")

greet_person({"name": "Alice", "city": "London"})
greet_person({"name": "Bob", "city": "New York"})
greet_person({"name": "Carol", "city": "Paris"})


def greet_person_2(person: dict[str, str]) -> None:
    match person.values():
        case ["Alice", city] as [*_, last_city]:
            print(f"Hello Alice and {last_city}!")
        case ["Bob", "b"]:
            print("Hello Bob!")
        case ("Charlie", *names) as [_first_name, *rest_names]:
            if rest_names:
                print(f"Hello {', '.join(rest_names)}!")
            else:
                print("Hello Charlie!")


greet_person_2({"name": "Alice", "city": "London"})
greet_person_2({"name": "Bob", "city": "New York"})
greet_person_2({"name": "Carol", "city": "Paris"})


def greet_person_3(person: dict[str, str], *, greeting: str = "Hi there!") -> None:
    match person.values():
        case ["Alice", city] as [*_, last_city]:
            print(f"{greeting}, Alice and {last_city}!")
        case ["Bob", "b"]:
            print(f"{greeting}, Bob!")
        case ("Charlie", *names) as [_first_name, *rest_names]:
            if rest_names:
                print(f"{greeting}, {', '.join(rest_names)}!")
            else:
                print(f"{greeting}, Charlie!")


greet_person_3({"name": "Alice", "city": "London"}, greeting="Heya!")
greet_person_3({"name": "Bob", "city": "New York"}, greeting="Howdy!")
greet_person_3({"name": "Carol", "city":