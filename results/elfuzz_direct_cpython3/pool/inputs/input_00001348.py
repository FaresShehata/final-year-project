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
    FAILURE   = "failure"

@runtime_checkable
class AsyncIter(Protocol[K]):
    def send(self, value: K) -> None: ...
    def throw(self, typ: type[BaseException], val: BaseException | None, tb: TracebackType | None) -> None: ...

async def gather(*aws: Awaitable[T]) -> list[T]:
    """Return a list of results in the order completed."""
    coros = [c for c in aws if isinstance(c, Coroutine)]
    syncs = [c for c in aws if not isinstance(c, Coroutine)]
    sync_results = await asyncio.gather(*syncs)
    return [*sync_results, *(await asyncio.wait_for(c, None) for c in coros)]

def is_iterable(obj: object) -> bool:
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True

# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=True)
class Node(Generic[K]):
    priority: int
    key: K
    # ... other attributes to be added as needed

@dataclasses.dataclass(frozen=True)
class Event(Generic[V]):
    timestamp: float
    event_type: str
    payload: V

@dataclasses.dataclass(frozen=True)
class GameRecord(Variant["GameRecord"]):
    player_id: str
    position: tuple[int, int]

@dataclasses.dataclass(eq=False, frozen=True)
class Player(Generic[V]):
    id: str
    name: str
    position_history: List[tuple[int, int]]

@dataclasses.dataclass(eq=False, frozen=True)
class Game(Generic[V]):
    players: List[Player]
    turn_order: Tuple[str, ...]

# ── Typing Generics ───────────────────────────────────────────────────────────

# Define the generic type `MyList` that can hold any type `T`
MyList[T] = List[T]

# Create an instance of `MyList` with type parameter `int`
my_list_int: MyList[int] = []

# Create an instance of `MyList` with type parameter `str`
my_list_str: MyList[str] = []

# ── Slots ─────────────────────────────────────────────────────────────────────

class Animal(Generic[K]):
    __