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
        case Book(_, _, _, 4.9): print("good")
        case Book(_, _, _, 1.7): print("poor")
        case Book(_, _, _, 2.4): print("mediocre")
        case Book(_, _, _, r):
            if not isinstance(r, float):
                raise TypeError("rating must be a float")
            print("unknown rating")


match_book(Book(title="Python Crash Course", author="Eric Matthes",
                 pages=460, rating=4.9738))
match_book(Book(title="Fluent Python", author="Luciano Ramalho",
                 pages=801, rating=-1))


# ─── Walrus Operator ─────────────────────────────────────────────────────────

greeting = 'Hello' if input('Enter your name: ') == 'Alice' else 'Hi'
print(greeting)


# ─── Typing Generics ─────────────────────────────────────────────────────────

async def fetch(url: str) -> bytes:
    ...  # implementation omitted


urls = ["https://example.com/page-1.html",
        "https://example.com/page-2.html"]

for url in urls:
    body = await fetch(url=url)
    print(body)


# ─── Exception Groups ────────────────────────────────────────────────────────

try:
    with open("/does/not/exist/file.txt") as file: pass
except OSError as e:
    print(e)
else:
    print("The file was found.")



# ── Constrained Types ────────────────────────────────────────────────────────<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>

class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __new__(
        cls,
        numer: int|float,
        denom: int=1,
        *,
        normalize: bool=True
    ) -> Rational:

        if denom == 0:
            raise ZeroDivisionError("zero denominator")

        num, den = (numer, denom) if numer >= 0 else (-numer, -denom)

        sign = +1 if num >= 0 else -1

        while num % 2 == 0 and den % 2 == 0:
            num //= 2
