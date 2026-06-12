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
            "status": self.status.name,
            "tags": self.tags,
            "metadata": self.metadata,
            "_history": [s.value for s in reversed(self._history)],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        kwargs = {
            "id": data["id"],
            "name": data["name"],
            "priority": getattr(Priority, data["priority"]),
            "status": getattr(Status, data["status"]),
            "tags": data.get("tags", []),
            "metadata": data.get("metadata", {}),
            "_history": [],
        }
        task = cls(**kwargs)
        task.transition(Status(data["_history"][-1]))
        return task


# ── Generics ──────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class Node[T_co]:
    value: T_co


@dataclasses.dataclass(frozen=True)
class Link[T_co]:
    next_node: Node[T_co]


@dataclasses.dataclass(frozen=True)
class List[T_co]:
    head: Node[T_co] = Node(None)
    tail: Node[T_co] = Node(None)

    def append(self, value: T_co) -> None:
        node = Node(value)
        if self.head == self.tail:
            self.head.next_node = node
            self.tail = node
            object.__setattr__(self, "head", node)
        else:
            self.tail.next_node = node
            self.tail = node

    def pop(self) -> T_co:
        assert not self.is_empty(), "list is empty"

        last_value = self.tail.value
        if self.head == self.tail:
            object.__setattr__(self, "tail", None)
            object.__setattr__(self, "head", Node(None))
        else:
            current = self.head
            while current.next_node != self.tail:
                current = current.next_node
            current.next_node = None
            object.__setattr__(self, "tail", current)

        return last_value

    def peek(self) -> T_co:
        assert not self.is_empty(), "list is empty"

        return self.head.next_node.value

    def extend(self, iterable: Iterable[T_co]) -> None:
        for item in iterable:
            self.append(item)

    def is_empty(self) -> bool:
        return self.head