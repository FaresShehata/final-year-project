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
    completed_at: float | None = None

    @property
    def running_time(self) -> float | None:
        if self.status.is_terminal():
            return time.time() - self.completed_at
        else:
            return None

    def update_status(self, new_status: Status) -> None:
        self.status = new_status
        self.completed_at = time.time()


def get_task(id: int) -> Task | None:
    return TASKS.get(id)


TASKS: dict[int, Task] = {}


async def complete_tasks() -> None:
    for task_id, task in list(TASKS.items()):
        if not task.running_time and task.status == Status.RUNNING:
            task.update_status(Status.SUCCESS)
            print(f"task {task.id} finished successfully")


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotDataClass:
    """This class has no special storage characteristics"""


@dataclasses.dataclass(slots=True)
class WithInitSlotDataClass:
    """This class has only slots with non-default values"""


@dataclasses.dataclass(slots=True)
class WithStrictSlotsDataClass:
    """This class has only slots without default value"""


# ── Structural Pattern Matching ───────────────────────────────────────────────

MATCH_DATA: dict[str, type[object]] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
}

def match_data(data: object) -> MatcherResult | None:
    for matcher, expected_type in MATCH_DATA.items():
        if isinstance(data, expected_type):
            return MatcherResult(matcher=matcher, actual=data)

    return None


@dataclasses.dataclass
class MatcherResult:
    matcher: str
    actual: object | None

    def __repr__(self) -> str:
        if self.actual is None:
            return f"<MatcherResult matcher={self.matcher}>"

        return f"<MatcherResult matcher={self.matcher}, actual={self.actual!r}>"



# ── Walrus Operator ───────────────────────────────────────────────────────────

def do_something(a: int, b: int) -> None:
    while a < 100:
        a += 1
        if b > 90:
            break
        elif b % 3 == 0:
            continue
        else:
            print("I'm doing something here...", end=" ")
            a -= 1
            yield b * a


# ── Generics & Typing ─────────────────────────────────────────────────────────

SAMPLE_LIST = [i for i in range(10)]
SAMPLE_SET = set(SAMPLE_LIST)
SAMPLE_TUPLE = tuple(i for i in range(10))
OTHER_SAMPLE_LIST = [i for i in range(20)]


class MyList(Generic[T]):
    """
    A simple generic list implementation.
    """

    def __init__(self, initial_values: list[T]) -> None:
        self.values = initial_values
        self.length = len(initial_values)

    def append(self, item: T) -> None:
        self.values.append(item)
        self.length += 1

    def pop(self) -> T:
        self.length -= 1
        return self.values.pop()

    def extend(self, items: Iterable[T]) -> None:
        for item in items:
            self.append(item)

    def remove(self, index: int) -> None:
        del self.values[index          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import os
import random as rando
import re
import shutil
import string
import sys
import time
import uuid
from collections.abc import (
    AsyncIterator,
    Awaitable,
    Callable,
