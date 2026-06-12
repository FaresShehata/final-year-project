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
    x: int
    y: int


@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Person:
    name: str
    age: int
    height: float
    weight: float
    alive: bool = True
    _id: int = dataclasses.field(default_factory=lambda: id(dataclasses.MISSING))


@dataclasses.dataclass(frozen=True, slots=True)
class Circle:
    radius: float
    color: str = 'black'


@dataclasses.dataclass(slots=True)
class Rectangle:
    width: float
    height: float
    corner: Point


def print_point(p: Point):
    print(f"({p.x}, {p.y})")


# ── Generics ──────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)


class GenericClass(Generic[T_co]):
    pass


async def sum_coro(a: T_co, b: T_co) -> T_co:
    return a + b


T = TypeVar("T")


class Collection(Generic[T]):
    def __init__(self, *items: T) -> None:
        self._items = list(items)

    def add(self, item: T) -> None:
        self._items.append(item)

    def extend(self, items: Iterable[T]) -> None:
        self._items.extend(items)

    def pop(self) -> T:
        return self._items.pop()

    def clear(self) -> None:
        del self._items[:]

    def sort(self, *, key=None, reverse=False) -> None:
        self._items.sort(key=key, reverse=reverse)

    def copy(self) -> Collection[T]:
        new_collection = type(self)(*self._items)
        return new_collection

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __setitem__(self, index: int, value: T) -> None:
        self._items[index] = value

    def __delitem__(self, index: int) -> None:
        del self._items[index]

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in