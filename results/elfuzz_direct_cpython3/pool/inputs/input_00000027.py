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
    A = 1
    B = 2


# ── Data structures ───────────────────────────────────────────────────────────

@runtime_checkable
class Sortable(Protocol[K]):
    """Sortable protocol.

    This class defines the contract for classes that can be sorted.
    """

    @classmethod
    def _compare(cls, a: K, b: K) -> int:
        raise NotImplementedError()


def insertionsort(array: list[K], *, compare: Callable[[K, K], int] | None = None) -> None:
    """Insertion sort algorithm."""
    if compare is None:
        compare = Sortable._compare
    n = len(array)
    for i in range(1, n):
        key = array[i]
        j = i - 1
        while j >= 0 and compare(key, array[j]) < 0:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key


@dataclasses.dataclass(frozen=True)
class Item():
    name: str
    weight: float
    value: int

colors = [
    ("red",   0.5),
    ("orange", 0.7),
    ("yellow", 0.9),
    ("green",  1.3),
    ("blue",   1.6),
    ("purple", 2.3),
]


def knapsack(size: int, items: list[Item]) -> int:
    """Knapsack problem using dynamic programming."""
    table = [[0] * (size+1)]
    for item in items:
        table.append([0] * (size+1))
    for i, v, w in items:
        for s in range(size+1):
            if w <= s:
                table[i+1][s] = max(table[i][s-w] + v, table[i][s])
            else:
                table[i+1][s] = table[i][s]
    return table[-1][-1]


class Sequence(Generic[T]):
    """"Sequence abstract base class."""

    def __getitem__(self, index: int) -> T:
        ...

    def __setitem__(self, index: int, value: T) -> None:
        ...

    def __delitem__(self, index: int) -> None:
        ...

    def __contains__(self, item: object) -> bool:
        ...

        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

