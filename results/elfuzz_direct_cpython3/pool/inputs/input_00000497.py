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
    def run(self) -> Awaitable[None]: ...


@runtime_checkable
class Waiter(Protocol[T]):
    def wait(self, timeout: float | None = ...) -> T: ...


@runtime_checkable
class Condition(Protocol[float]):
    def wait(self, condition: Callable[[float], bool]) -> float: ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Post:
    title: str
    body: str
    user: User


@dataclasses.dataclass(frozen=False)
class Comment:
    content: str
    post: Post
    user: User


@dataclasses.dataclass(frozen=True, slots=True)
class PostCounter:
    count: int
    posts: list[str]


# ── Generics ───────────────────────────────────────────────────────────────────

class SomeGeneric(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get_value(self) -> T:
        return self.value


# ── Walrus Operator ────────────────────────────────────────────────────────────

def _foo(x: int | None) -> int:
    return x or 42


# ── Typing Generics ────────────────────────────────────────────────────────────

async def main() -> None:
    print((1 + 3) / (7 - 2))

    await asyncio.sleep(1.0)


@overload
def foo(x: int) -> int: ...


@overload
def foo(x: float) -> float: ...


def foo(x: int | float) -> int | float:
    if isinstance(x, int):
        return 2 * x
    else:
        return 2 * x


@overload
def bar(x: int, y: int) -> tuple[int, int]: ...


@overload
def bar(x: float, y: float) -> tuple[float, float]: ...


def bar(x: int | float, y: int | float) -> int | float | tuple[int | float, int | float]:
    if isinstance(x, int):
        return x ** 2, y **