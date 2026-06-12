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
    x : int
    y : int

    def move_up(self):
        self.y += 1


# ── Slots ────────────────────────────────────────────────────────────────────

class PointSlots(Point):
    __slots__ = ("x", "y")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(obj: K | None, *patterns: tuple[K, V]) -> V | None:
    for value, result in patterns:
        if value == obj or (isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return None


def match_with_default(obj: K | None, default: V, patterns: tuple[tuple[K, V]]) -> V | None:
    for value, result in patterns:
        if value == obj or (value is not None and isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return default


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def count_to_3() -> Iterator[int]:
    yield 1
    a := yield 2
    yield 3


async def main():
    async for i in count_to_3():
        print(i)


# ── Generics ──────────────────────────────────────────────────────────────────

def merge_dicts(*dicts: dict[str, int]) -> dict[str, int]:
    """Merge multiple dictionaries into one."""
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


merge_dicts(
    {"a": 1}, {"b": 2},
    {"c": 3}, {"d": 4}
)

list_of_numbers = [i for i in range(int(input()))]

numbers = list(map(lambda n: n + 1, filter(lambda n: n % 2 == 1, map(lambda x: x ** 2, list_of_numbers))))


class MyList(list[T]):
    ...
    

# ── Exception Group ───────────────────────────────────────────────────────────

class HTTPError(Exception):
    status_code: int

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

    
class AppError(Exception):
    http_error: HTTPError

    def __init__(self, message: str