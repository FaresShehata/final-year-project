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
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


# ── Generics ──────────────────────────────────────────────────────────────────

class Foo(Generic[T]):
    pass


Foo[int].bar = 42           # works!
# Foo[str].bar = 42         # error!


# ── Async/await ──────────────────────────────────────────────────────────────

async def sleep(t: int) -> None:
    await asyncio.sleep(t / 1000)


def fib_async(n: int) -> Awaitable[int]:
    if n < 2:
        return n
    return fib_async(n-1) + fib_async(n-2)


async def fib_iter_async():
    yield 1
    if n := await fib_async(1): yield n
    i = 1
    while True:
        if n := await fib_async(i): yield n
        i += 1


# ── Walrus Operator ───────────────────────────────────────────────────────────

a, b = 1, 2
x = (c := a + b, a := b, b := c)[-1]


# ── Pattern Matching ──────────────────────────────────────────────────────────

match ["apple"]:
    case ["pear"]:
        print("pineapple!")
    case ["banana", *fruits]:
        print("ok!", fruits)
    case _:
        print("nope!")


class MatchTest:
    def __init__(self) -> None:
        self.a = 3
        self.b = 7
        self.c = 10
        self.d = 8
        self.e = 9


t = MatchTest()
match t:
    case MatchTest(a=x, d=y):
        print(x+y)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def greet(name: str | None) -> str:
    match name:
        case None:
            return 'Hello, stranger!'
        case "Alice":
            return f'Hi, Alice!'
        case _:
            return 'Hello stranger :)'


def find_index(lst: list[str], value: str) -> int | None:
    match lst:
        case []:
            return None
        case [first, *rest] if first == value:
            return 0
        case [first, *rest]:
            index = find_index(rest, value)
            if index is not None:
                return index + 1
            else:
                return None


def nested_match(value: Any) -> None:
    match value:
        case {"foo": foo} as foo_map:
            print(foo_map["foo"])
        case {"bar": bar}:
            print(bar)
        case _:
            pass


class Person:
    def __init__(self, name: str) -> None:
        self.name = name
        self.next_person = None

    def __str__(self) -> str:
        return self.name


p1 = Person('John')
p2 = Person('Jane')
p3 = Person('Jim')
p1.next_person = p2
p2.next_person = p3


class Node:
    def __init__(self, value: T, next_node=None) -> None:
        self.value = value
        self.next = next_node


root_node = Node(42, next_node=Node(666))


class List:
    def __init__(self, head: Node) -> None:
        self.head = head

    def __iter__(self) -> Iterator[Any]:
        node = self.head
        while node:
            yield node.value
            node = node.next