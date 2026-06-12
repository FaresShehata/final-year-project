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
    status: Status = Status.PENDING
    tags: list[str] = []
    metadata: dict = {}
    history: list[Status] = []

    def transition(self, new_status: Status) -> None:
        self.history.append(self.status)
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

Foo = namedtuple("Foo", ["a", "b"], defaults=(None, ""))


# ── Classes ───────────────────────────────────────────────────────────────────

class Bar:
    def __init__(self, a: int, b: str = "") -> None:
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return f"Bar(a={self.a}, b={self.b})"


# ── Generics and Type Variables ────────────────────────────────────────────────

def find_max_min_in_list(lst: list[int]) -> tuple[int, int]: ...
def find_max_min_in_tuple(tpl: tuple[int, ...]) -> tuple[int, int]: ...


# ── Exceptions and Groups ─────────────────────────────────────────────────────

async def get_something() -> str: ...

try:
    await get_something()
except Exception as e:
    print(type(e), e.args)


# ── Walrus Operator ───────────────────────────────────────────────────────────

myvar = ... if some_condition else None


# ── Type Annotations and Type Checking ────────────────────────────────────────

def my_function(arg1: int, arg2: str | bool) -> str: ...


# ── Type Aliases ──────────────────────────────────────────────────────────────

MyTypeAlias: type = List[int]


# ── Type Hints and Type Inference ─────────────────────────

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

