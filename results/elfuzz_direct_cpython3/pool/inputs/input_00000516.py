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


# ── Protocols ───────────────────────────────────────────────────────────────────

@runtime_checkable
class HasLength(Protocol[K]):
    def __len__(self) -> int: ...


@runtime_checkable
class HasElems(Generic[T], Protocol):
    @property
    def elems(self) -> list[T]: ...


# ── Dataclasses ──────────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Point(dataclasses.DataClassMixin):
    x: float
    y: float


PointD = dataclasses.make_dataclass(
    name="Point",
    fields=(
        ("x", float),
        ("y", float),
    ),
)


def point_repr(point: PointD) -> str:
    return f"({point.x}, {point.y})"


# ── Slots ───────────────────────────────────────────────────────────────────────


@dataclasses.dataclass(slots=True)
class DataclassWithSlots:
    foo: str = dataclasses.field()
    bar: int = dataclasses.field()


# ── Structural Pattern Matching ──────────────────────────────────────────────────


@dataclasses.dataclass(order=True)
class FooBarBaz:
    foo: str = dataclasses.field(compare=False)
    bar: int = dataclasses.field(compare=False)
    baz: float = dataclasses.field(default=4.3)


def match_foo_bar_baz(foo_bar_baz: FooBarBaz) -> None:
    """This function works with Python < 3.11"""
    match foo_bar_baz:
        case FooBarBaz(foo='foo', bar=bar, baz=baz) if foo == 'foo' and bar > 100:
            print('found a FooBarBaz')
        case _ as other:
            print(f'matching failed with value: {other}')


# ── Walrus Operator ─────────────────────────────────────────────────────────────


async def main() -> None:
    start_time: float = time.perf_counter()

    # Not supported on CPython versions < 3.8
    await asyncio.wait_for(asyncio.shield(asyncio.sleep(1)), timeout=None)

    end_time: float = time.perf_counter()
    elapsed_time: float = end_time - start_time
    print(elapsed_time)


async def main_1() -> None:
    start_time: float = time.perf_counter()

    # Supported from CPython version