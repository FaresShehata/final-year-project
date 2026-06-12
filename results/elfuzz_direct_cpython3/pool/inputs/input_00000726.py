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


@dataclasses.dataclass(order=True, frozen=True, order_using=lambda obj: (obj.x, obj.y))
class FrozenPoint(Point): ...


@dataclasses.dataclass(order=True, frozen=True, repr=False, eq=False, order_using=lambda obj: obj.x)
class ComparableFrozenPoint(FrozenPoint): ...


@dataclasses.dataclass(frozen=True)
class UnserialisableDataclass:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class SerializableDataclass:
    name: str
    age: int
    fav_numbers: list[int] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class StringifiedSerializableDataclass(SerializableDataclass):
    """This class can be serialized and deserialized using JSON."""

    _str_repr: ClassVar[str]

    @property
    def _dict_repr(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "StringifiedSerializableDataclass": ...

    @classmethod
    def deserialize(cls, s: str) -> "StringifiedSerializableDataclass":
        ...


# ── Slots ─────────────────────────────────────────────────────────────────────

# Using a `__slots__` attribute will allow us to save memory by not having the
# object store a dictionary of its attributes. The trade-off is that we have to
# use `attr.ib()` instead of `dataclasses.field()`.
#
# We can also add type hints for the attributes.
#
# Note that this does not affect objects created after the class definition.

@dataclasses.dataclass(frozen=True)
class WithSlots:
    id: str
    name: str
    age: int
    _private_attr: int

    __slots__: ClassVar[tuple] = ("id", "name", "_private_attr")


class WithoutSlots:
    id: str
    name: str
    age: int
    _private_attr: int


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_string(s: str) -> int:
    if len(s) == 0:
        return 3
    elif s[0].isupper():
        return 4
    else:
        return len(s)

def compare_strings(a: str, b: str) -> int:
    return -1 if len(b) < len(a) else 1

def match_list(l: list[T]) -> T:
    match l:
        case []:             ...
        case [a]:            return a
        case [a, *b]:        return a + match_list(b)
        case [_]:            raise ValueError("Empty lists are forbidden.")
        case _:              raise ValueError("Other cases are forbidden.")

def match_point(point: Point) -> tuple[K, V]:
    match point:
        case Point(x=a, y=b):      return a, b
        case Point(x=0, y=y):      return 0,