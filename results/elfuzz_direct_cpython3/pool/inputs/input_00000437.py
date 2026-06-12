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
    
    def __init__(self, firstname: str, lastname: str, age: int, company: str, position: str) -> None:
        super().__init__(firstname=firstname, lastname=lastname, age=age)
        self.company = company
        self.position = position


PersonDict = dict[str, Person]
EmployeeDict = dict[str, Employee]

person_dict: PersonDict = {}
employee_dict: EmployeeDict = {}

for i in range(10_000):
    if i % 2 == 0:
        person_dict[f"p{i}"] = Person(firstname=f"f{i}", lastname=f'l{i}', age=i)
    else:
        employee_dict[f'e{i}'] = Employee(
            firstname="f",
            lastname="l",
            age=46,
            company="Google",
            position="CEO",
        )

print(person_dict["p9"].age > employee_dict['e8'].age)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def get_class_name(obj: object) -> str:
    class_name = obj.__class__.__name__
    if class_name.startswith("__"):
        return f"{obj.__class__.__module__}.{class_name}"
    return class_name


P = TypeVar("P", bound=object)
Q = TypeVar("Q", bound=object)

class SomeClass(P):
    def some_method(self) -> str:
        return 'some method'


class OtherClass(Q):
    def another_method(self) -> str:
        return 'another method'


def match_object(obj: object) -> str:
    match obj:
        case SomeClass():
            return f"This is a {get_class_name(SomeClass)}"
        
        case OtherClass():
            return f"This is a {get_class_name(OtherClass)}"

        case _:
            return "Unknown object"


# ── Walrus Operator ──────────────────────────────────────────────────────────

my_dict = {"a": 1}

result = my_dict.get("b", default=None) if result := my_dict.get("a") else None

print(result)


# ── Generics ──────────────────────────────────────────────────────────────────

class MyGeneric(Generic[T]):
    ...


# ── Exception Groups ──────────────────────────────────────────────────────────

try:
    raise ValueError("foo")
except ValueError as err:
    group = ExceptionGroup("error