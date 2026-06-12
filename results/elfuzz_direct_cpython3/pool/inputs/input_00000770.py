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
        case Book(title="The Great Gatsby", author=author):
            print(author)
        case Book(title=title, author="J.K. Rowling"):
            print(title)
        case _ if book.rating > 4.5:
            print("Wow!")
        case _ if not isinstance(book.isbn, str):
            print("Invalid ISBN!")

# ── Walrus operator ───────────────────────────────────────────────────────────

async def do_work() -> None:
    while True:
        result = await get_data_from_db()
        if result is False:
            break
        else:
            process_result(result)


def get_data_from_db() -> bool:
    if some_condition:
        return True
    else:
        return False


# ── Generics ───────────────────────────────────────────────────────────────────

class MultiSet(Generic[T]):
    def __init__(self, *values: T) -> None:
        self._items = values[:]

    def add(self, item: T) -> None:
        self._items.append(item)

    def remove(self, item: T) -> None:
        try:
            self._items.remove(item)
        except ValueError as error:
            raise KeyError(error.args[0])

    def discard(self, item: T) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            pass

    def clear(self) -> None:
        del self._items[:]

    def union(self, other: Iterable[T]) -> MultiSet[T]:
        return MultiSet(*set(self._items).union(set(other)))

    def intersection(self, other: Iterable[T]) -> MultiSet[T]:
        return MultiSet(*set(self._items).intersection(set(other)))

    def difference(self, other: Iterable[T]) -> MultiSet[T]:
        return MultiSet(*set(self._items).difference(set(other)))

    def symmetric_difference(self, other: Iterable[T]) -> MultiSet[T]:
        return MultiSet