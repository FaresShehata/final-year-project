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


# ── Classes ───────────────────────────────────────────────────────────────────

@runtime_checkable
class AsyncIterable(Protocol[K]):
    """Represent an asynchronous iterable."""

    @overload
    async def acall(self) -> AsyncIterable[K]: ...  # type: ignore[misc]
    @overload
    async def acall(self, *args: tuple[V]) -> K: ...
    async def acall(self, *args): ...


@dataclasses.dataclass(frozen=True)
class Stats(Timer):
    total: int = 0

    def update(self, n: int = 1) -> None:
        self.total += n

    def reset(self) -> None:
        object.__setattr__(self, "_start", time.time())
        object.__setattr__(self, "total", 0)


def assert_not_none(x: T | None) -> T:
    if x is None:
        raise ValueError("x cannot be None")
    return x


class Timer(Generic[T], Generic[T]):
    """Timer.

    Usage:

    >>> t = Timer()
    >>> with t.timer():
    ...     pass
    """

    _START: ClassVar[float] = 0.0

    def __init__(self) -> None:
        self._end: float | None = None

    def timer(self) -> T:
        end = time.time() - self._START
        self._end = end
        return end

    def elapsed(self) -> float:
        if self._end is not None:
            return self._end
        else:
            return time.time() - self._START

    def reset(self) -> None:
        self._end = None

    def __enter__(self) -> Timer[T]:
        self._START = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._END = time.time()

    def __int__(self) -> int:
        return round(int(self.elapsed()))

    def __float__(self) -> float:
        return int(self.elapsed())

    def __str__(self) -> str:
        return f"{self.elapsed():.3f}"

    def __repr__(self) -> str:
        return self.__str__()


async def wait_for_async(
    coros_or_fut: list[Awaitable[None]] | Awaitable[list[None]],
    /,
