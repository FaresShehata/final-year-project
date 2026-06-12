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
    def from_dict(cls, d: dict) -> Self: ...  # noqa E704


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=True)
class UserAccount:
    username: str
    email: str
    status: Status; _gt_ = (Status.PENDING, Status.RUNNING)


# ── Slots ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class FileStat:
    size: int
    modified_time: float


# ── Structural Pattern Matching ──────────────────────────────────────────────

def get_class_name(obj: object) -> str:
    match obj:
        case list():
            return "List"
        case dict():
            return "Dict"
        case set():
            return "Set"
        case _:  # default case
            return type(obj).__name__

print(get_class_name([]))

match "hello":
    case "abc":
        print("a")
    case "xyz":
        print("b")
    case _:
        print("c")


# ── Walrus Operator ──────────────────────────────────────────────────────────

for i in range(5):
    match i:
        case 0:
            continue
        case 1:
            break
        case _:
            break

while True:
    match i := input("> "):
        case "":
            break
        case _:
            continue

# ── Generics ────────────────────────────────────────────────────────────────

class Array(TypedDict):
    items: List[Any]

array: Array[str] = {"items": ["apple", "banana"]}

# ── Exceptions ───────────────────────────────────────────────────────────────

async def long_running_task(delay: float) -> None:
    await asyncio.sleep(delay)

async def run_tasks(delay_list: List[float]) -> None:
    tasks = []
    try:
        for delay in delay_list:
            task = asyncio.create_task(long_running_task(delay))
            tasks.append(task)
    except Exception as e:
        for task in tasks:
            task.cancel()

run_tasks([1.0, 2.0])

# ── Exception Groups ─────────────────────────────────────────────────────────

try:
    with open("/path/to/file.txt"):
        raise ValueError("Invalid file contents")
except ExceptionGroup as exc_group:
    "UserLogEntry",
    ["timestamp", "level", "message"],
)
TimestampedMessage = tuple[float, str]

# ── ParamSpec ────────────────────────────────────────────────────────────────

F = ParamSpec("F") # A placeholder for a function's parameters.

def map_to_string(func: F) -> Callable[F, str]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        result = func(*args, **kwargs)
        if isinstance(result, str):
            return result
        else:
            return str(result)
    return wrapper