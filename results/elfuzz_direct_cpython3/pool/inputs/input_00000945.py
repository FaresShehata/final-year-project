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


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Address:
    street_number: str
    street_name: str
    city: str


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    last_name: str
    age: int
    address: Address
    friends: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    isbn: int
    rating: float = 0.0


# ── Slots ─────────────────────────────────────────────────────────────────────

Person.__slots__ = ("name", "last_name")
Book.__slots__ = ("title", "author")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person) -> None:
    match person:
        case Person(name="John Smith"):
            print("Hello John!")
        case Person(last_name="Doe"):
            print("Hi there!")
        case _:
            print("Welcome!")


def match_book(book: Book) -> None:
    match book:
        case Book(title="The Hitchhiker's Guide to the Galaxy",
                  author="Douglas Adams", isbn=978-0345396424):
            print("This is a classic!")
        case Book(_, _, isbn=isbn, rating > 4.5):
            print("This is a fantastic book!")
        case _:
            print("We don't know about this book.")


# ── Walrus Operator ───────────────────────────────────────────────────────────

def count_words(text: str) -> Counter[str]:
    result: Counter[str] = Counter()
    while word := text.pop():
        result[word] += 1
    return result


# ── Generics ───────────────────────────────────────────────────────────────────

class Queue(Generic[K]):
    def __init__(self) -> None:
        self._elements: list[tuple[float, K]] = []

    def enqueue(self, key: K, priority: float = 0.0) -> None:
        index = bisect.bisect_left([e[0] for e in self._elements], priority)
        self._elements.insert(index, (priority, key))

    def dequeue(self) -> K:
        return self._elements.pop()[1]

    def pop_all(self) -> list[K]:
        elements = self._elements.copy()
        self.clear()
        return [element[1] for element in elements]

    def clear(self) -> None:
        self._elements.clear()


class PriorityQueue(Generic[T]):
    def __init__(self) -> None:
        self._queue: list[tuple[float, T]] = []
        self._index: int = 0

    def insert(self, item: T, priority: float = 0.0) -> None:
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def remove_first(self) -> T:
        return heapq.heappop(self._queue)[2]

    def remove_last(self) -> T:
        return self._queue.pop()[2]

    def remove_by_index(self, index: int) -> T:
        value = self._queue[index]
        del self._queue[index]
        return value

    def pop_all(self) -> list[T]:
        queue = self._queue.copy()
        self.clear()
        return [