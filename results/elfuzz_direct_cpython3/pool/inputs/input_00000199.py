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
    LOW      = -1  # low priority
    NORMAL   = 0   # normal (default) priority
    HIGH     = 1   # high priority


@runtime_checkable
class Repr(Protocol[K]):
    @property
    def repr(self: K) -> str: ...


# ─── Classes ────────────────────────────────────────────────────────────────

# partial class demo
class Partial(Generic[T]):
    def __init__(self, func: Callable[[T], T]) -> None:
        self.func = func
    
    def __call__(self, *args: T.args, **kwargs: T.kwargs) -> T:
        return self.func(*args, **kwargs)


@dataclasses.dataclass
class Person:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Point:
    x: float
    y: float


# ────── Functions ───────────────────────────────────────────────────────────
def identity(x: T) -> T:
    return x


async def sleep_async(seconds: float | int = 1.0) -> float:
    await asyncio.sleep(seconds)
    return seconds


# ─────── Asyncio ───────────────────────────────────────────────────────────-

async def main() -> None:
    print(await sleep_async())
    print(sleep_async())


async def make_polls(n: int = 4) -> list[dict[str, int]]:
    polls = [
        {"id": i, "vote_count": 0} for i in range(random.randint(3, n+1))
    ]
    return polls

async def poll(polls: Iterable[dict[str, int]]) -> dict[str, V]:
    # TODO: implement polling
    raise NotImplementedError()

async def update_votes(votes: dict[str, int], polls: list[dict[str, int]]) -> dict[str, V]:
    # TODO: implement updating votes
    raise NotImplementedError()


# ─────── Data classes ───────────────────────────────────────────────────────-

# https://docs.python.org/3/library/dataclasses.html
@dataclasses.dataclass(order=True)
class NamedThing:
    id_num: int
    metadata: dict[str, str] = dataclasses.field(default_factory=dict)

    def get_metadata(self) -> str:
        result = ""
        if self.metadata:
            result += f"metadata: {json.dumps