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

    def get_distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
    

PointList = list[Point]

@dataclasses.dataclass(frozen=True)
class PointDict:
    points: dict[int, Point]

    def __getitem__(self, key: int) -> Point: ...
    
    def __iter__(self): ...

    def __len__(self): ...




# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotExample:
    __slots__ = ["x", "_y"]

    def __init__(self, x: float, y: float):
        self._x, self._y = x, y
    
    @property
    def x(self) -> float:
        return self._x
    
    @x.setter
    def x(self, value: float):
        self._x = value
    
    @property
    def y(self) -> float:
        return self._y
    
    @y.setter
    def y(self, value: float):
        self._y = value


# ── Structural Pattern Matching ───────────────────────────────────────────────

class Shape(Generic[T]):
    def area(self) -> T: ...

@dataclasses.dataclass
class Circle(Shape[float]):
    radius: float

    def area(self) -> float:
        return math.pi * self.radius**2
    

def match_shape(shape: Shape[T]) -> None:
    match shape:
        case Shape() as s: print(s.area())
        case Circle(radius=r): print(r)
        case _: print("unknown")


# ── Walrus Operator ───────────────────────────────────────────────────────────
#
# The walrus operator can be used to assign a variable in the same expression.

async def fetch(url: str) -> str:
    await asyncio.sleep(random.random())
    return url

urls = [
    ("https://example.com",),
    ("https://google.com"),
    ("https://stackoverflow.com/questions/38649785"),
]

start_time = time.monotonic()

for url in urls:
    if html := await fetch(*url):
        print(html)
print(time.monotonic() - start_time)


# ── Generics ──────────────────────────────────────────────────────────────────

def chunked(iterable: Iterable[T], n: int) -> Iterator[list[T]]:
    """ Yield successive `n`-sized chunks from `iterable`. """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice