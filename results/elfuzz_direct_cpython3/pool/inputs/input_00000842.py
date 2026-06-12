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

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority
    status: Status
    start_time: float = dataclasses.field(default_factory=time.time)
    end_time: float = dataclasses.field(
        default=dataclasses.MISSING, compare=False, init=False)


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class PointSlots:
    x: float
    y: float

    def distance_slots(self, other: PointSlots) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(x: list[str]): ...
match(["apples", "pears", "bananas"]): ...
match({}) : ...  # type: ignore
match(None): ...  # type: ignore


class MatchType(enum.Enum):
    A = 1
    B = 2
    C = 3


def match_type(a: int, b: int, c: int) -> None:
    match a, b, c:
        case _ if a == 0 and b == 0 and c == 0:
            print("a,b,c are all zero!")
        case _ if a > 0 or b < 0:
            print(f"a={a},b={b},c={c}")
        case MatchType.A | MatchType.B as v, MatchType.C as w:
            print(v * w)
        case v, w if v > w:
            print(f"{v} is greater than {w}")
        case 1, 2, 3:
            print("one two three")
        case _:
            print("nothing matched")


# ── Walrus Operator ───────────────────────────────────────────────────────────

def get_data() -> tuple[int, str]: ...

data = get_data()

while total := sum(data[0]) != total / len(data[0]):
    # do stuff with the total
    pass


# ── Generics ──────────────────────────────────────────────────────────────────

async def gather(task_list: list[Awaitable[T]]) -> list[T]:
    tasks = [asyncio.create_task(t) for t in task_list]
    await asyncio.wait(tasks)
    return [t.result() for t in tasks]


# ─