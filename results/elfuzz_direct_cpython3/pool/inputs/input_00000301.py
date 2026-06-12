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
            "metadata": self.metadata,
            "_history": [h.value for h in self._history],
        }

    @classmethod
    def from_dict(
        cls, d: dict[str, T], *, default_priority: Priority = Priority.NORMAL
    ) -> Task:
        task_id = d["id"]
        task_name = d["name"]

        try:
            task_priority = getattr(Priority, d["priority"]).value
        except KeyError as e:
            raise ValueError(f"Invalid priority: {e}") from e

        task_tags = d.get("tags") or []
        task_metadata = d.get("metadata") or {}

        return cls(
            task_id,
            task_name,
            Priority(task_priority),
            Status(d["status"]),
            task_tags,
            task_metadata,
            default_priority=default_priority,
        )


@dataclasses.dataclass
class Person:
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float
    description: str = ""
    email_addresses: frozenset[str] = dataclasses.field(default_factory=frozenset)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self.first_name}, {self.age}, {self.gender}"

    def __hash__(self) -> int:
        return hash((self.first_name, self.last_name)) ^ self.age

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Person):
            return all(
                [
                    self.first_name == other.first_name,
                    self.last_name == other.last_name,
                    self.age == other.age,
                ]
            )
        elif isinstance(other, tuple):
            return all([self.first_name == v[0], self.last_name == v[1]])
        else:
            return NotImplemented

    def __contains__(self, item: str) -> bool:
        if isinstance(item, str):
            return any(i in item for i in (self.first_name, self.last_name))
        return super().__contains__(item)

    def __iter__(self) -> Iterator[Any]:
        yield from self.__dict__.values()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclasses.dataclass
class Student        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
