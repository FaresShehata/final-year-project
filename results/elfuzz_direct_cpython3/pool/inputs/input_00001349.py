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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        if not isinstance(data.get("priority"), str):
            raise TypeError(f"Expected 'str', got '{type(data['priority'])}' instead.")
        elif data["priority"].upper() == "LOW":
            priority = Priority.LOW
        elif data["priority"].upper() == "NORMAL":
            priority = Priority.NORMAL
        elif data["priority"].upper() == "HIGH":
            priority = Priority.HIGH
        elif data["priority"].upper() == "URGENT":
            priority = Priority.URGENT
        else:
            raise ValueError("Invalid priority value.")

        return cls(id=data["id"], name=data["name"], priority=priority)


# ── Slots ─────────────────────────────────────────────────────────────────────


def create_slots(**kwargs: T) -> tuple[T]: ...


@dataclasses.dataclass(slots=True)
class Person:
    ...


@dataclasses.dataclass(frozen=True, slots=True)
class Product:
    ...


person_a = dataclasses.replace(Person(name="Alice", age=30), age=31)
product_b = dataclasses.replace(Product(title="Bread", price=4.99), title="Butter")
print(person_a)  # person_a: Person(name='Alice', age=31)
print(product_b)  # product_b: Product(title='Butter', price=4.99)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person) -> Tuple[int, str]:
    match person:
        case Person(name=name, age=age):
            return name.upper(), age

        case Person(age=age, name=None):
            return f"{age} years old with no name.", None

        case _:
            return "Unknown person."


# ── Walrus Operator ───────────────────────────────────────────────────────────

# pre-3.8:
# x = i := 1

counter: Counter = Counter()

for item in items:
    counter[item] += 1

# post-3.8:
for item in items:
    if item in counter:
        counter[item] += 1
    else:
        counter[item] = 1


# ── Typing Generics ───────────────────────────────────────────────────────────

async def fetch(url: str) -> str:
    """This function asynchronously fetches the content of a URL."""
    await asyncio.sleep(random.randint(1, 5))  # Simulate an asynchronous operation.
    return url


fetch_result: str = await fetch("http://example.com")


# ── Exception Groups ──────────────────────────────────────────────────────────

try:
    raise ExceptionGroup(
        title="Multiple errors occurred",
        exceptions=[
            ZeroDivisionError(),
            IndexError(),
            NameError(),
        ],
    )
except Exception as e:
    print(e)  # ExceptionGroup(title="Multiple errors occurred", exceptions=[ZeroDivisionError(), IndexError(), NameError()])
    for ex in e.exceptions:
        print(ex)  # ZeroDivisionError(), IndexError(), NameError()


# ── Asyncio Tasks ─────────────────────────────────