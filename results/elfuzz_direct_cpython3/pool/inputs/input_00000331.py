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
            "id":       self.id,
            "name":     self.name,
            "priority": self.priority.value,
            "status":   self.status.value,
            "tags":     self.tags,
            "metadata": self.metadata,
            "history":  self._history,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Task:
        return cls(
            id=d["id"],
            name=d["name"],
            priority=Priority(d["priority"]),
            status=Status(d["status"]),
            tags=d.get("tags", []),
            metadata=d.get("metadata", {}),
        )


# ── Slots ────────────────────────────────────────────────────────────────────

class NamedPoint:
    __slots__: tuple[str, ...] = ("_name", "_point")

    def __init__(self, name: str, point: Point) -> None:
        self._name = name
        self._point = point

    @property
    def name(self) -> str:
        return self._name

    @property
    def point(self) -> Point:
        return self._point

    @classmethod
    def from_point(cls, name: str, point: Point) -> NamedPoint:
        return cls(name, point)

    def __repr__(self) -> str:
        return f"NamedPoint({self.name}, {self.point})"


# ── Structural Pattern Matching ───────────────────────────────────────────────

def compare_task(ta: Task, tb: Task) -> bool:
    return ta.name == tb.name and ta.priority == tb.priority and ta.tags == tb.tags


def match_tasks(tasks: list[Task]) -> list[Task]:
    tasks.sort(key=lambda t: t.priority)
    unique_tasks: list[Tuple[int, Task]] = [(t.id, t) for t in tasks if not any(compare_task(ta, t) for ta in tasks)]
    result: list[Task] = []
    while unique_tasks:
        _, task = unique_tasks.pop()
        result.append(task)
        task.transition(Status.RUNNING)
        for i, other_task in enumerate(filter(lambda t: t != task, tasks)):
            if compare_task(task, other_task):
                del tasks[i]
    return result


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def long_running_function(n: int) -> str

def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

