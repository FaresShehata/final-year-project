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


@runtime_checkable
class Comparable(Protocol[K]):
    def __lt__(self: K, other: K | int) -> bool:
        ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class StockTicker:
    ticker: str
    price: float


@dataclasses.dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: float


@dataclasses.dataclass(eq=True, frozen=True)
class User:
    username: str
    email: str
    age: int


# ── Async/await ───────────────────────────────────────────────────────────────

async def double(n: int) -> int:
    await asyncio.sleep(1.0)
    return 2 * n


def run_async() -> None:
    """Async example."""
    print("\n\nRun async")

    loop = asyncio.get_event_loop()
    time1 = time.time()

    result = loop.run_until_complete(asyncio.gather(
        double(1),
        double(3),
        double(7)))
    
    assert result == [2, 6, 14]
    print(time.time() - time1)


# ── Slots ────────────────────────────────────────────────────────────────────

class Post:

    __slots__ = ("title", "content")

    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content


# ── Structural Pattern Matching ───────────────────────────────────────────────

def validate_number(number: int) -> bool:
    match number:
        case 1:
            print("one")
        case 2:
            print("two")
        case _:
            print("other")


def display_product(product: dict[str, any]) -> None:
    match product:
        case {"id": 1}:
            print("First!")
        case {"id": 2}:
            print("Second!")
        case {"id": 3}:
            print("Third!")
        case {"name": name} if len(name) < 5:
            print(f"Short name: {name}")
        case {"price": p} if type(p) != int:
            print(f"Not an integer: {p}")
        case {"id": i,