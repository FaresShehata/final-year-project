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

    def to_dict(self) -> dict[str, any]: ...
    @classmethod
    def from_dict(cls, data: dict) -> SerializableDataclass: ...


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotDataclass:
    a: int
    b: int
    c: int

    def __post_init__(self):
        assert isinstance(self.a, int), f"Expected `a` to be an integer but got `{type(self.a).__name__}`."
        assert isinstance(self.b, int), f"Expected `b` to be an integer but got `{type(self.b).__name__}`."
        assert isinstance(self.c, int), f"Expected `c` to be an integer but got `{type(self.c).__name__}`."

    def __repr__(self) -> str: ...


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(obj: any) -> None:
    if isinstance(obj, list):
        print("Is a list.")
    elif isinstance(obj, tuple):
        print("Is a tuple.")
    else:
        print("Not a list or tuple.")

match([3, 4])  # Is a list.
match((3, 4))  # Is a tuple.


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def example_01() -> None:
    async for i in count():
        print(i * 4)  # 0, 4, 8, 12, etc.

async def example_02() -> None:
    while True:
        t = await get_temperature()
        if t < 19.7 and t > 16.0:
            break

async def example_