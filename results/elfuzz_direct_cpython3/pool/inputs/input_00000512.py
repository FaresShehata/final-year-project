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
    def from_dict(cls, data: dict) -> "Task":
        if not isinstance(data.get("priority"), str):
            raise TypeError(f"Expected 'str', got '{type(data['priority'])}' instead.")
        elif data["priority"].upper() == "LOW":
            priority = Priority.LOW
        elif data["priority"].upper() == "NORMAL":
            priority = Priority.NORMAL
        elif data["priority"].upper() == "HIGH":
            priority = Priority.HIGH
        elif data["priority"].upper() == "URGENT":
            priority = Priority.URGENT
        else:
            raise ValueError("Invalid priority value.")

        return cls(id=data["id"], name=data["name"], priority=priority)


# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    __slots__ = ("age", "height", "weight")

    def __init__(self, age: int, height: int, weight: int) -> None:
        self.age      = age
        self.height   = height
        self.weight   = weight


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_value(x: int | str, y: int | str) -> str:
    match (x, y):
        case (a : str, b : str):
            return f"{a} and {b}"
        case (a : str, b : int):
            return f"{a} and {y}"
        case (b : int, a : str):
            return f"x={y}, y={a}"
        case (a , c) :
            return f"{a} and {c}"

    # default clause
    return "unmatched"


def match_type_and_value(x: int | str, y: int | str) -> str:
    match (x, y):
        case (a:int, b : int):
            return f"a:{a} and b:{b}"
        case (a:str, b : str):
            return f"a:{a} and b:{b}"
        case (a:int, b : str) | (a:str, b : int):
            return f"other cases"
        case (_, _) :
            return "not matched"

    # default clause
    return "unmatched"


def match_multiple_types(a: int | str, b: int | str) -> str:
    match (a, b):
        case (                task.transition(Status.RUNNING)
                task.tags.extend(["in-progress"])
                task.metadata["start"] = time.time()
                try:
                    result = await asyncio.wait_for(
                        task_runner(task), timeout=random.uniform(0.2, 1.9) * 10
                    )
                    print(result)
                except RuntimeError as e:
                    task.transition(Status.FAILED)
                    task.tags.extend(["error"])
                    task.metadata.update({"end": time.time(), "error": e})
                else:
