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
    def from_dict(cls, d: dict[str, any]) -> T: ...


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    pages: int
    rating: float

    def format_pages(self) -> str:
        if self.pages < 1000:
            return f"{self.pages}p"
        else:
            return f"{self.pages // 1000}k"


@dataclasses.dataclass(slots=True)
class Point:
    x: int
    y: int
    z: int = 0


# ─── Generics ────────────────────────────────────────────────────────────────

_T = TypeVar("_T")


def find_max(values: list[_T], key: Callable[[_T], V] = lambda v: v) -> _T:
    max_value: _T | None = None
    for value in values:
        if max_value is None or key(max_value) < key(value):
            max_value = value
    return max_value


# ─── Structural Pattern Matching ─────────────────────────────────────────────

def decode_protocol(protocol: bytes) -> str:
    match protocol:
        case b"JSON":
            return "JSON"
        case b"XML":
            return "XML"
        case b"CSV" | b"TSV" as encoding:
            return f"{encoding.decode('ascii')} - {len(encoding)}"
        case (b"HTML", version) as html:
            return f"<{html[0]}>{version}"
        case _:  # fallthrough
            raise ValueError("Unknown protocol")


# ─── Walrus Operator ─────────────────────────────────────────────────────────

async def wait_for_seconds(seconds: int) -> None:
    await asyncio.sleep(seconds)


async def main() -> None:
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        print(f"Current elapsed time: {elapsed:.2f}s")
        if elapsed > 3.0:
            break
        await wait_for_seconds(random.randint(1, 4))


asyncio.run(main())


# ─── Typing Generics ─────────────────────────────────────────────────────────

def count_duplicates(items: Iterable[_T]) -> tuple[int, Counter[_T]]:
    counter: Counter[_T] = Counter()
    for item in items:
        counter[item] += 1
    duplicates_count = sum(count for _, count in counter.items()) - len(counter.keys())
    return duplicates_count, counter


# ─── Exception Groups ─────────────────────────────────────────────────────