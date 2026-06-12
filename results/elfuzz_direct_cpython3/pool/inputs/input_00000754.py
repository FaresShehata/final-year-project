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


@dataclasses.dataclass(frozen=True, order=True, slots=True)
class NamedTuplePoint(Point): ...  # type: ignore # https://github.com/python/mypy/issues/7396

@dataclasses.dataclass(frozen=True, order=True, slots=True)
class MyDataClass:
    tag: str
    value: int
    timestamp: float = dataclasses.field(default_factory=time.time)


# ── Slots ────────────────────────────────────────────────────────────────────

class Node(Generic[K]):
    parent: Node[K] | None = None

    def __init__(self, value: K) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class BinaryNode(Node[int]):
    left_child: BinaryNode[int] | None = None
    right_child: BinaryNode[int] | None = None

    def insert(self, value: int) -> None:
        if value < self.value:
            if not self.left_child:
                self.left_child = BinaryNode(value)
            else:
                self.left_child.insert(value)
        elif value > self.value:
            if not self.right_child:
                self.right_child = BinaryNode(value)
            else:
                self.right_child.insert(value)
        else:
            raise ValueError(f"{value=} already exists")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def search(sequence: list[int], target: int) -> int | None:
    for index, element in enumerate(sequence):
        if element == target:
            return index
        return None


def safe_search(sequence: list[int], target: int) -> int | None:
    match sequence:
        case []       :
            return None
        case [_first, *rest]:
            if first == target:
                return 0
            else:
                rest_index = safe_search(rest, target)
                return rest_index + 1 if rest_index is not None else None


def safe_binary_search(sequence: list[int], target: int) -> int | None:
    low, high = 0, len(sequence) - 1
    while low <= high:
        mid = (low + high) // 2
        match sequence[mid]:
            case v if v == target:
                return mid
            case v if v < target:
                low = mid + 1
            case v if)
assert test_struct.y == b"TE\0ST\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"

# ── Struct and array ──────────────────────────────────────────────────────────
struct_test = struct.pack("<I", 0xDEADBEEF)
array_test = array.array("B", [0xE, 0xD, 0xA, 0xB, 0xF])
print(struct_test.hex())
assert struct.unpack("<I", struct_test)[0] == 0xDEADBEEF
assert array_test[0] == 0xE and array_test[-1] == 0xF

# ── Memory view ──────────────────────────────────────────────────────────────
#
mem_view = memory