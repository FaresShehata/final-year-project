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
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
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
            priority=getattr(Priority, data["priority"]),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


# ── Named Tuples ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Foo:
    a: int
    b: str = ""
    c: list[float] = dataclasses.field(default_factory=list)


# ── Classes ───────────────────────────────────────────────────────────────────

class MyIterable(Generic[K, V]):
    def __iter__(self) -> Iterator[Tuple[K, V]]:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> Tuple[K, V]:
        raise NotImplementedError

    def keys(self) -> Iterable[K]:
        for _, v in self:
            yield v

    def values(self) -> Iterable[V]:
        for k, _ in self:
            yield k

    def items(self) -> Iterable[Tuple[K, V]]:
        for k, v in self:
            yield k, v

    def clear(self) -> None:
        raise NotImplementedError

    def popitem(self) -> Tuple[K, V]:
        raise NotImplementedError

    def remove(self, item: Tuple[K, V]) -> None:
        raise NotImplementedError

    def append(self, item: Tuple[K, V]) -> None:
        raise NotImplementedError

    def insert(self, index: int, item: Tuple[K, V]) -> None:
        raise NotImplementedError

    def __delitem__(self, index: int) -> None:
        raise NotImplementedError

    def __setitem__(self, index: int, value: Tuple[K, V]) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class MyAsyncIterator(MyIterable[G, H], AsyncIterable[H]):
    def __aiter__(self) -> AsyncIterator[H]:
        return self



# ── Generics ──────────────────────────────────────────────────────────────────

def generic_identity(x: T) -> T:
    return x


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def foo() -> int:
    while True:
        try:
            await asyncio.sleep(.25)
        except asyncio.CancelledError:
            break
        print((x := 42))
        assert x == 42
    return 43


async def
    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
