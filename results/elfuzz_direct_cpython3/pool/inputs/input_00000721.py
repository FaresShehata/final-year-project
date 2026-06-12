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

    def __str__(self): ...

    def __repr__(self): ...
# end of dataclasses:


# ── Slots ─────────────────────────────────────────────────────────────────────

@daclass(time=8.64e-3)
class Item:
    name: str
    count: int
    d: float

    def value(self) -> float:
        return self.count * self.d

    def __post_init__(self): ...

    # added by magic class: __eq__
    def __eq__(self, item: object) -> bool:
        if isinstance(item, Item):
            return hash(self) == hash(item)
        else:
            return NotImplemented

    # added by magic class: __lt__
    def __lt__(self, item: object) -> bool:
        if isinstance(item, Item):
            return hash(self) < hash(item)
        else:
            return NotImplemented

    # added by magic class: __hash__
    def __hash__(self) -> int:
        return hash((self.name, self.count))

    # added by magic class: __call__
    def __call__(self, n: int) -> Item:
        return Item(name=self.name, count=n, d=self.d)


@daclass
class Book:
    title: str
    authors: list[str]
    price: float

    def get_price(self) -> float:
        return round(self.price, 2)

    def __str__(self) -> str:
        return f"{self.title} ({', '.join(self.authors)})"


@daclass
class Article:
    title: str
    author: str
    content: str
    date: float

    def __str__(self) -> str:
        return f"Article: {self.author}: {self.title}"


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_article(article: Article) -> None:
    match article:
        case Article(title="Python", author="Guido van Rossum"):
            print("Python was written by Guido van Rossum")
        case Article(title="Java", author="James Gosling"):
            print("Java was written by James Gosling")
        case _:
            print(f"No info about the author")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def main() -> None:
    async with open("./docs/example.txt", "w