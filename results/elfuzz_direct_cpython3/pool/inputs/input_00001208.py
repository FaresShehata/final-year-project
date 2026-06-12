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


# ── Types ────────────────────────────────────────────────────────────────────


@runtime_checkable
class Traceback(Protocol):
    @property
    def filename(self) -> str: ...
    @property
    def line(self) -> int: ...
    @property
    def func(self) -> str: ...


def get_traceback(exc: BaseException) -> Traceback | None:
    tb = exc.__traceback__
    while tb is not None:
        try:
            if isinstance(tb.tb_frame.f_globals['__name__'], str):
                return tb.tb_frame.f_globals.copy().pop('__name__', '')
            break
        except AttributeError:
            pass
        tb = tb.tb_next
    return None


# ── Exceptions ────────────────────────────────────────────────────────────────


class MyError(Exception):
    """My error."""


class ErrorGroup(ExceptionGroup):
    """An exception group."""

    def __init__(
        self,
        base_exception: BaseException,
        *exceptions: BaseException,
        description: str = "",
    ) -> None:

        super().__init__(*exceptions, description=description)
        self.base_exceptions = tuple(exceptions)
        self.base_exception = base_exception


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclasses.dataclass(slots=True)
class Point:
    x: float
    y: float


# ── Data Classes with Slots ───────────────────────────────────────────────────
@dataclasses.dataclass(frozen=True, slots=True)
class Person:
    name: str
    age: int
    gender: str
    height: float


# ── Generics ──────────────────────────────────────────────────────────────────


class Query(Generic[T]):
    def __init__(self, condition: Callable[[T], bool]) -> None:
        self._condition = condition

    def filter(self, item: T) -> bool:
        return self._condition(item)


# ── Asyncio ──────────────────────────────────────────────────────────────────


async def wait_for_seconds(seconds: int) -> None:
    await asyncio.sleep(seconds)


async def main():
    ...


# ── Walrus Operator ──────────────────────────────────────────────────────────


value = (x := 3 + 4, x ** 2)[0]  # value == 7 and x == 7
print(value, type(value))  # 7 <class 'int'>


# ── Structural Pattern Matching ───────────────────────────────────────────────


def match(num: int) -> str:
    match num