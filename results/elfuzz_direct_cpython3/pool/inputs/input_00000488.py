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
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Task:
        if not isinstance(data["priority"], Priority):
            raise ValueError(f"Invalid task priority: {data['priority']}")
        if not isinstance(data["status"], Status):
            raise ValueError(f"Invalid task status: {data['status']}")
        return cls(
            id=data["id"],
            name=data["name"],
            priority=data["priority"],
            status=data["status"],
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


# ── Slots ─────────────────────────────────────────────────────────────────────

class UserMeta:
    max_age: float = 3600 * 24 * 7  # 1 week


class User(Generic[K], ProtoUserMixin, metaclass=UserMeta):
    # slots exclude class attributes and methods
    __slots__ = ("key", "__age", "__name")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def find_first(predicate: Callable[[any], bool], items: Iterable[T]) -> T | None:
    for item in items:
        if predicate(item):
            return item
    return None


x: int | str = "hello world"


class A:
    pass


class B(A):
    pass


b = B()
a = A()


match b:
    case A():
        print("B is a subclass of A")
    case B():
        print("It's an instance of B")


def get_candy(age: int) -> Candy:
    if age <= 18:
        return ChildrenCandy()

    elif age <= 65:
        return AdultCandy()

    else:
        return SeniorCandy()


candy: Candy = get_candy(19)


# ── Walrus Operator ───────────────────────────────────────────────────────────

numbers: set[int]

for number in range(-10, 11):
    if found := numbers.add(number):
        print(f"Found duplicate: {found}")

print(numbers)


# ── Typing Generics ───────────────────────────────────────────────────────────

class LinkedList(typing.Generic[T]):
    head: Node[T]
    tail: Node[T]


class Node(typing.Generic[T]):
    value: T
    next: Optional[Node[T]] = None


# ── Exception Groups ─────────────────────────