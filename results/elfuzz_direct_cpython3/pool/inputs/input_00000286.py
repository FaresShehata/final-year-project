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


class Direction(enum.IntEnum):
    NORTH     = 0
    EAST      = 90
    SOUTH     = 180
    WEST      = 270
    NORTHEAST = 45
    SOUTHWEST = 315
    NORTHWEST = 135
    SOUTHEAST = 225


def print_status(status: Status) -> None:
    print(f"status={str(status).lower()}")


print_status(Status.PENDING)
print_status(Status.RUNNING)
print_status(Status.SUCCESS)
print_status(Status.FAILED)
print_status(Status.CANCELLED)


@runtime_checkable
class Nameable(Protocol[K]):
    name: K


@overload
def get_name(nameable: Nameable[K]) -> K: ...


@overload
def get_name(nameable: object) -> str | None: ...


def get_name(nameable: Nameable[str] | object) -> str | None:
    if isinstance(nameable, Nameable):
        return nameable.name
    else:
        return None


class Person(Nameable["Person"]): ...  # type: ignore


person = Person()
person.name = "Alice"


name = get_name(person)
print(name)

name = get_name(object())
print(name)


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Named:
    first_name: str
    last_name: str


@dataclasses.dataclass(slots=True, frozen=True)
class FrozenNamed:
    first_name: str
    last_name: str


frozen_named = FrozenNamed(first_name="Bob", last_name="Smith")


person = Named(first_name="John", last_name="Doe")

print(isinstance(person, Named))
print(isinstance(person, FrozenNamed))


# ── Structural Pattern Matching ───────────────────────────────────────────────

match person:
    case Named(first_name="John", last_name="Doe"): ...
    case Named(last_name="Cooper") as p: ...


match direction := Direction.NORTHWEST:
    case Direction.NORTHWEST:
        print("the cardinal point of the compass")


# ── Walrus Operator ───────────────────────────────────────────────────────────

sum(
    i
    for i in range(10_000)
    if (i % 2 == 0)
    and (i > 2
    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
