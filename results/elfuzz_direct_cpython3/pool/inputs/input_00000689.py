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
class Person:
    name:      str
    age:       int
    children:  list[Person]

    @property
    def grandchildren(self) -> list[Person]:
        return [g for c in self.children for g in c.grandchildren] if self.children else []

    def __post_init__(self):
        assert len(set(self.name)) == len(self.name), f"Duplicate chars found in name '{self.name}'!"


@dataclasses.dataclass(frozen=True)
class Note:
    text: str
    creator: str
    timestamp: float
    status: bool = True

    def toggle_status(self) -> None:
        self.status ^= True

    def __bool__(self) -> bool:
        return self.status


@dataclasses.dataclass(slots=True)
class TodoItem:
    description: str
    done: bool = False

    def __post_init__(self):
        assert isinstance(self.done, bool)


# ── Generics ───────────────────────────────────────────────────────────────────

def gen_list() -> tuple[type[T], ...]:
    return (str, int, float)

GenListType = TypeVar("GenListType", *gen_list())

def map_list(lst: list[GenListType]) -> list[GenListType]:
    return [*map(str, lst)]


# ── Walrus Operator ────────────────────────────────────────────────────────────

counters: dict[str, Counter[K]] = {}

async def get_count_value(key: K) -> Counter[int]:
    counter = await counters.get(key, Counter())
    counter[key] += 1
    counters[key] = counter
    return counter

@overload
def count_item(item: T, key_func: Callable[[T], K]) -> Counter[int]: ...
@overload
def count_item(item: Iterable[T], key_func: Callable[[T], K]) -> Counter[int]: ...
def count_item(item: T | Iterable[T], key_func: Callable[[T], K] | None = lambda x: x) -> Counter[int]:
    key_to_counter: dict[K, Counter[int]] = {}
    counter_key: K
    for item_ in item:
        key_to_counter.setdefault(key_func(item_), Counter()).update([item_])
    return sum(map(lambda c: c[1][key_func(c[0])] or 0, key_to_counter.items()))


# ── Structural