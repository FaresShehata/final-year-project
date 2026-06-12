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

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=4)


def task_example() -> None:

    p1 = Point(x=-3.69, y=1.78)
    p2 = Point(x=1.59, y=-3.32)

    print(f"Distance between points p1 and p2 is {p1.distance(p2):.2f}")

    t1 = Task(id=1, name="Task 1")
    t2 = Task(id=2, name="Task 2", priority=Priority.URGENT)
    t3 = Task(id=3, name="Task 3", status=Status.RUNNING)
    t4 = Task(name="Task 4", status=Status.FAILED)
    t5 = Task(name="Task 5", priority=Priority.HIGH, tags=["tag1", "tag2"])

    print(t1 > t2)
    print(t2 < t3)
    print(t2 >= t4)
    print(t3 <= t2)


# ── Slots ─────────────────────────────────────────────────────────────────────

class PointSlot:
    __slots__: tuple[str, ...] = ("x", "y")


def point_slot_example() -> None:

    p1 = PointSlot(x=-3.69, y=1.78)
    p2 = PointSlot(x=1.59, y=-3.32)

    print(f"Distance between points p1 and p2 is {PointSlot.distance(p1, p2):.2f}")


# ── Structural Pattern Matching ────────────────────────────────────────────────

def pattern_matching_tutorial() -> None:

    class Cat: ...
    class Dog: ...
    class Bird: ...

    animals = [Cat(), Dog(), Cat()]

    for animal in animals:
        match animal:
            case Cat():
                print("Meow")
            case Dog():
                print("Woof")
            case Bird():
                print("Tweet")
            case _:  # default clause matches everything else
                print("Unknown animal species")


# ── Walrus Operator ───────────────────────────────────────────────────────────

def walrus_operator_example() -> None:

    fruits = ["Apple", "Banana", "Cherry"]
    result = next((fruit for fruit in fruits if not fruit.startswith("B")), "")

    assert result == "Apple"


# ── Generics ──────────────────────────────────────────────────────────────────

def generic_example() -> None:

    class Stack[T]:
        def __init__(self) -> None:
            self.stack_list: list[T] = []

        def push(self, item: T) -> None:
            self.stack_list.append(item)

        def pop(self) -> T:
            return self.stack_list.pop()

        def peek(self) -> T:
            return self.stack_list[-1]

        def is_empty(self) -> bool:
            return len(self.stack_list) == 0


    stack_int = Stack[int]()
    stack_str = Stack[str]()


# ── Exception Groups ───────────────────────────────────────────────────────────

def exceptions_group_example() -> None:

    try:
        raise ValueError("ValueError")
    except ValueError as err:
        egroup = ExceptionGroup(
            f"Exception Group",
            [
                err,
                RuntimeError("RuntimeError"),
                SyntaxError("SyntaxError"),
            ],
        )
        raise egroup


# ── dataclasses and enums example ──────────────────────────────────────────────

def enum_dataclasses_example() -> None:

    @dataclasses.dataclass
    class Person:
        name: str
        age: int

    people = [Person("Alice", 30), Person("Bob", 25)]
    name_counts = Counter(person.name for person in people)

    for name, count in name_counts.items():
        print(f"{name}: {count} times")


def main() -> None:
    task_example()
    point_slot_example()
    pattern_matching_tutorial()
    walrus_operator_example()
    generic_example()
    exceptions_group_example()
    enum_dataclasses