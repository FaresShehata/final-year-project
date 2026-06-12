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
    x : int
    y : int

    def move_up(self):
        self.y += 1


# ── Slots ────────────────────────────────────────────────────────────────────

class PointSlots(Point):
    __slots__ = ("x", "y")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(obj: K | None, *patterns: tuple[K, V]) -> V | None:
    for value, result in patterns:
        if value == obj or (isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return None


def match_with_default(obj: K | None, default: V, patterns: tuple[tuple[K, V]]) -> V | None:
    for value, result in patterns:
        if value == obj or (value is not None and isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return default


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def do_something() -> int:
    await asyncio.sleep(0.1)
    return 42


result = (a := await do_something()) + a


# ── Generics ──────────────────────────────────────────────────────────────────

class Cache(Generic[T]):
    _cache: dict[str, T]

    def __init__(self) -> None:
        self._cache = {}

    def get(self, key: str) -> T | None:
        return self._cache.get(key)

    def put(self, key: str, value: T) -> None:
        self._cache[key] = value


class CacheWithExpirationDate(Generic[T]):
    _cache: dict[str, T]
    _expiration_dates: dict[str, float]

    def __init__(self) -> None:
        self._cache = {}
        self._expiration_dates = {}

    def get(self, key: str) -> T | None:
        expiration_date = self._expiration_dates.get(key)
        if expiration_date is None or time.time() < expiration_date:
            return self._cache.get(key)

    def put(
        self, key: str, value: T, expires_at: float | None = None
    ) -> None:
        self._cache[key] = value
        if expires_at is not None:
            self._expiration_dates[key] = expires_at


# ── Exception Groups ──────────────────────────────────────────────────────────

class DatabaseException(Exception): ...
class NetworkException(Exception): ...
class ServerException(Exception): ...

exception_group = ExceptionGroup(
    "general",
    [DatabaseException(), NetworkException(), ServerException()],
)


# ── Exercise ──────────────────────────────────────────────────────────────────

@overload
def print_hello(name: str, once: Literal[True]) -> None: ...
@overload
def print_hello(name: str, once: Literal[False] = False) -> None: ...
def print_hello(name: str, once: bool = True) -> None:
    hello_string = f"Hello, {name}!"
    with open("/dev/stdout") as stdout_file:
        print(hello_string, file=stdout_file, flush=True)
    if not once:
        return


print_hello("World")
print_hello("Friend", once=True)