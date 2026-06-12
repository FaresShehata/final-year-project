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


@overload
def do_something(a: int) -> str: ...
@overload
def do_something(f: Callable[[int], int]) -> int: ...

async def do_something(a: int|Callable[[int], int]) -> int|str:
    if callable(a): a = await a()
    return f"do something with {a}"


# ─── Data classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False)
class OrderedDataClass:
    k: K
    v: V

    def __post_init__(self) -> None:
        assert self.k > self.v, "k must be greater than v"


@dataclasses.dataclass(init=False, order=True, repr=False)
class UnhashableOrderedDataClass:
    k: K
    v: V

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super(UnhashableOrderedDataClass, cls).__new__(cls)
        instance.__dict__.update(kwargs)
        return instance

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnhashableOrderedDataClass):
            raise TypeError(f"{type(other)} is unorderable")
        return hash(self) == hash(other)


@dataclasses.dataclass(slots=True, init=True, order=True, repr=False)
class SlotsDataClass:
    k: K
    v: V

    def __post_init__(self) -> None:
        assert self.k > self.v, "k must be greater than v"


# ── Structural Pattern Matching ───────────────────────────────────────────────

class MatchException(Exception):
    pass


def match(obj: object) -> None:
    try:
        if obj is None or isinstance(obj, (bool, float, int)):
            print(f"{obj} is a number")
        elif isinstance(obj, str):
            print(f"'{obj}' is a string")
        else:
            print(type(obj))
    except MatchException as e:
        print(e)


match(None)
match(True)
match(42.5)
match("hello world!")
match([3])
match({"key": {"value":"test"}})
match({})


# ── Walrus Operator ───────────────────────────────────────────────────────────

x = 37
y = x + 5 if (x := 42        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)
            self.sort_key = min((i.sort_key for i in self._data), default=-float("inf"))

    def clear(self) -> None:
        self._data.clear()

    def pop(self, index: int = -1) -> T:
        return self._data.pop(index)

    def remove(self, item: T) -> None:
