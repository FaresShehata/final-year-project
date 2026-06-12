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
    ("blue",  0.4),
    ("green", 0.3),
]

items = [Item(name=name, weight=weight, value=value * priority.value)
         for weight, color in colors
         for name, priority, value in [("hat",  Priority.A, 1_000),
                                       ("shirt", Priority.B, 600),
                                       ("pants", Priority.A, 800),
                                       ("shoes", Priority.B, 900)]]


async def main():
    start_time = time.perf_counter()

    # ── Sorting algorithms ─────────────────────────────────────────────────────

    items.sort(key=lambda item: (item.weight, item.name))
    print("Sorted by weight:", ", ".join(map(str, items)))

    heap = []
    for item in items:
        heapq.heappush(heap, (-item.weight, item.name))  # Convert to min-heap
    print("Sorted by negative weight:", ", ".join(heapq.heapreplace(heap, tuple(item))[1] for item in items))

    # ── Generics ───────────────────────────────────────────────────────────────

    # Define generic types T and U
    T = TypeVar("T")
    U = TypeVar("U")

    # Create a new class using the Generic metaclass; declare type variables as parameters
    @dataclasses.dataclass
    class Pair(Generic[T, U]):
        first: T
        second: U
    
    my_pair = Pair[int, str](first=3, second="hello")

    # ── Structural Pattern Matching ────────────────────────────────────────────
    
    match items[0]:
        case Item(name='shirt', weight=_, value=700): 
            print('Found the shirt!')
        case _:
            print('Did not find the shirt.')

    # ── Walrus Operator ────────────────────────────────────────────────────────

    x = 1
    y = 2
    result = f"{x:=d} {y:=b}"  # Equivalent to `result = f"{x=:#d} {y=:#b}"`
    print(result)

    # ── Typing Generics ────────────────────────────────────────────────────────

    # See https://docs.python.org/3/library/typing.html#generics
    
    # Declare type variable