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
    def from_dict(cls, d: dict[str, any]) -> T: ...


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    pages: int
    rating: float

    def info(self) -> tuple[str]:
        return (self.title, self.author)


book1 = Book(title="Python Crash Course", author="Eric Matthes",
             pages=460, rating=4.9738)
print(book1.info())


# ─── Slots ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int = 0


p1 = Person(name="John Doe")
p2 = dataclasses.replace(p1, name="Jane Doe")
print(dataclasses.asdict(p1))
print(dataclasses.astuple(p1))
print(p1 == p2)


# ─── Structural Pattern Matching ─────────────────────────────────────────────

def match_book(book: Book) -> None:
    match book:
        case Book(title=t, author=a, pages=p, rating=r):
            print(f"{t} by {a}, {p} pages, {r:.2f}")
        case _:
            print("No such book")


match_book(Book(title="The Great Gatsby", author="F. Scott Fitzgerald",
                pages=180, rating=4.00))


# ─── Walrus Operator ─────────────────────────────────────────────────────────

def fib(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    while True:
        yield b
        for i in range(a + b, n):
            b += i - a
        a, b = b, n


async def main() -> None:
    gen = fib(10)
    while True:
        try:
            await asyncio.sleep(random.random())
            v = next(gen)  # note that this is for data-only values, not for side effects
            print(v)
        except StopIteration as e:
            break


asyncio.run(main())


# ─── Typing Generics ─────────────────────────────────────────────────────────

def max_by_key(items: list