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
class Comparable(Protocol[K]):
    def __lt__(self, other: K) -> bool: ...
    def __le__(self, other: K) -> bool: ...
    def __gt__(self, other: K) -> bool: ...
    def __ge__(self, other: K) -> bool: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    height: float


@dataclasses.dataclass(frozen=False)
class Address:
    street: str
    city: City


@dataclasses.dataclass(slots=True)
class User:
    """
    >>> u1 = User(name="Alice", address=Address(street="Main Street", city=City.Moscow))
    >>> u1.address.street
    'Main Street'
    >>> u1.name = "Bob"  # TypeError: can't set attribute
    """
    name: str
    address: Address


@dataclasses.dataclass(slots=True)
class Employee(User):
    role: Role


@dataclasses.dataclass(slots=True)
class City:
    name: str


@dataclasses.dataclass(slots=True)
class Role:
    title: str


# ── Generics and typing ───────────────────────────────────────────────────────-

T1 = TypeVar("T1")
T2 = TypeVar("T2")


def concat(a: T1, b: T2) -> tuple[T1, T2]:
    return a, b


class Stack(Generic[T]):
    _items: list[T]

    def __init__(self) -> None:
        self._items = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T:
        return self._items[-1]

    def empty(self) -> bool:
        return len(self._items) == 0

    def length(self) -> int:
        return len(self._items)


class Queue(Generic[T]):
    _items: deque[T]


# ── Walrus operator ───────────────────────────────────────────────────────────

def filter_by_age(
    users: list[User],
    min_age: int = 