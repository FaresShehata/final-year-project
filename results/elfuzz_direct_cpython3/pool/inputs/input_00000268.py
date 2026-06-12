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
    
    def update_status(self, new_status: Status) -> None:
        assert new_status.is_terminal() or self.status == Status.RUNNING
        if new_status.is_terminal():
            self._history.append(new_status)
            self.status = new_status
        else:
            raise ValueError(f"cannot change task status from {self.status} to {new_status}")

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        self.tags.remove(tag)


def read_data(filename: str) -> list[Task]:
    with open(filename) as f:
        tasks_json_lines = [json.loads(line.strip()) for line in f]
    tasks = []
    for task_data in tasks_json_lines:
        task = Task(**task_data)
        tasks.append(task)
    return tasks


# ── Slots & Structural Pattern Matching ───────────────────────────────────────

class Person(Generic[T]):
    __slots__: ClassVar[tuple[str]] = ("name", "_age")

    def __init__(self, name: T, age: int = 30) -> None:
        self.name = name
        self._age = age
    
    def get_age(self) -> int:
        return self._age
    

@overload
def get_age(person: Person[int]) -> int: ...
@overload
def get_age(person: Person[float]) -> float: ...
@overload
def get_age(person: Person[str]) -> str: ...
def get_age(person: Person[T]) -> T:
    match person:
        case Person(name="Alice", age=int(age)) when age > 18:
            return "Adult"
        case Person(name=name, age=age):
            return f"{name} ({age})"
        case _:
            return "Unknown"


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def countdown(n: int) -> None:
    while n > 0:
        print(n)
        await asyncio.sleep(1)
        n -= 1
    print("done")


async def execute_tasks(tasks: list[Runnable], progress_bar: bool = False) -> None:
    loop = asyncio.get_event_loop()
    completed: set[Runnable] = set()

    async def check_completed(runnable: Runnable) -> bool:
        try:
            result = await runnable.run()
            print(f"[