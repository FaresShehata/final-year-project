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


@dataclasses.dataclass(eq=True, order=True)
class Student:
    name: str
    age: int
    grades: list[float]

    def average_grade(self) -> float:
        return sum(self.grades) / len(self.grades)


@dataclasses.dataclass(slots=True)
class Person:
    """Class with private attribute."""

    _name: str

    def get_name(self) -> str:
        return self._name.upper() if self._name else ""

    def set_name(self, new_name: str) -> None:
        self._name = new_name[:255]

    def __repr__(self) -> str:
        return f"<Person(name={self.get_name()}, ...>"

    def __str__(self) -> str:
        return f"Name: {self.get_name()}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotObject(object):
    __slots__ = ["_x", "_y"]

    def __init__(self, x: int, y: int) -> None:
        self.set(x, y)

    def set(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return not (self == other)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f'<SlotObject(x={self._x}, y={self._y})>'


# ── Structures Pattern Matching ───────────────────────────────────────────────

def match_x_or_y(
    x_or_y: int | float,
    on_x: Callable[[int], None],
    on_y: Callable[[float], None]
) -> None:
    if isinstance(x_or_y, int):
        on_x(x_or_y)
    elif isinstance(x_or_y, float):
        on_y(x_or_y)
    else:
        raise TypeError(f"{x_or_y=} must be an integer or float.")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def fib(n: int) -> int:
    a, b = 0, 1
    while True:
        if a >= n:
            return a
        yield b
        a, b = b, a + b


async def main():
    print("\n\nWALRUS OPERATOR 🦊")
    async for i in fib(4294967296): ...
    print(i)

    print("END WALRUS OPERATOR 🐨\n")


asyncio.run(main())


# ── Generics ──────────────────────────────────────────────────────────────────

def average(xs: Iterable[T]) -> float:
    return sum(xs) / len(xs)


def mean(xs: tuple[int, ...] | list[int]) -> float:
    return sum(xs) / len(xs)


# ── Exception Groups ──────────────────────────────────────────────────────────

async def sleep(n: float) -> None:
    await asyncio.sleep(n)


async def run_tasks(tasks: list[Callable[..., Awaitable]]) -> None:
    group = asyncio.ExceptionGroup()

    for task in tasks:
        group.add_exception_group(task())

    await group


tasks = []
for i in range(10):
    tasks.append(lambda: sleep(random.random()))

try:
    asyncio.run(run_tasks(tasks))
except RuntimeError as e:
    print(e)


# ── TypedDict ─────────────────────────────────────────────────────────────────

<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        # The following code will fail at run-time if the type of value isn't compatible with T.
        assert isinstance(value, T), f"{value=} must be {T}."
        setattr(obj, self.priv, value)


class min_length(_Constrained):
    """Annotate a string field so its length is at least N."""
    
    def __init__(self, n: int):
        super().__init__()
        self.n = n

    def __set__(self, obj, value: str):
        super().__set__(obj, value)
        assert len(value) >= self.n, f'{value=} must have minimum length {self.n}.'


class max_length(min_length):
    """Annotate a string field so its length is at most N."""

    def __init__(self, n: int):
        super().__init__(n=n)


class min_bytes(_Constrained):
    """Annotate a bytes field so it's at least this long in bytes."""
    
    def __init__(self, n: int):
        super().__init__()
        self.n = n

    def __set__(self, obj, value: bytes):
        super().__set__(obj, value)
        assert len(value) >= self.n, f'{value=} must have minimum length {self.n}.'


class max_bytes(min_bytes):
    """Annotate a bytes field so it's at most this long in bytes."""


class min_float(_Constrained):
    """Annotate a number field so it has more than N fractional digits."""

    def __init__(self, n: int):
        super().__init__()
        self.n = n

    def __set__(self, obj, value: float):
        super().__set__(obj, value)
        sign        = abs(value * min(1e-320, 1e+320))
        frac_digits = -1 * math.floor(math.log(sign, 10)) + min(32, max(-32, self.n))
        assert frac_digits < 32 and frac_digits > 0, \
               f'value {value=:.{frac_digits}f} must have frac_digits <= 32.'


class max_float(min_float):
    """Annotate a number field so it's less than this many fractional digits."""

    def __init__(self, n: int):
