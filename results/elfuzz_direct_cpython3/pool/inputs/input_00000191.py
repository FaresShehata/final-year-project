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
class Iterable(Protocol[K]):
    """Iterable protocol."""

    def __iter__(self: Iterable[K]) -> Iterator[K]:
        ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str


@dataclasses.dataclass(frozen=False)
class Planet:
    name: str
    moons: tuple[str, ...]


@dataclasses.dataclass(order=True, frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str


@dataclasses.dataclass(eq=True, order=True, frozen=True)
class Employee(Person):
    department: str
    salary: float


@dataclasses.dataclass(order=True, frozen=True)
class Card:
    number: int
    issuer: str
    balance: float


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotUser:
    name: str
    age: int


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_pattern(value: T, patterns: list[tuple[Callable[[T], bool], Callable[[T], V]]] | None = None) -> V:
    if not isinstance(patterns, list):
        patterns = [(lambda _: True, lambda x: x)]

    for is_match, transform in patterns:
        if is_match(value):
            return transform(value)


def match_type(obj: object, types: list[type[T]]) -> bool | V | None:
    for t in types:
        if isinstance(obj, t):
            return t()

    return False


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def do_something() -> None:
    print(await asyncio.sleep(random.random()))


async def main():
    await do_something()


# ── Generics ──────────────────────────────────────────────────────────────────

@overload
def get_most_common(items: list[V], k: Literal[0]) -> dict[V, int]: ...
@overload
def get_most_common(items: list[V], k: int) -> list[tuple[V, int]]: ...


def get_most_common(
