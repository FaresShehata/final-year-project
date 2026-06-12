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


class Direction(enum.IntEnum):
    NORTH     = 0
    EAST      = 90
    SOUTH     = 180
    WEST      = 270
    ROTATE_90 = 90
    ROTATE_180 = 180
    ROTATE_270 = 270


@enum.unique
class Color(enum.Enum):
    RED   = (1, 'r')
    GREEN = (2, 'g')
    BLUE  = (3, 'b')


# ── Protocol ────────────────────────────────────────────────────────────────

# @runtime_checkable
class Comparable(Protocol[T]):
    def __lt__(self: T, other: OtherType) -> bool:
        ...


class Item:

    def __init__(self, count: int):
        self.count = count

    def __repr__(self):
        return f"<Item({self.count})>"


class CountableList(list[Comparable]):

    def add(self, item: Comparable):
        if isinstance(item, Comparable):
            super().append(item)
        else:
            raise TypeError(f"{item} is not a valid comparable type")


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class OrderedDataClass:

    """Ordered data class with default values."""

    status: str = "Pending"


@dataclasses.dataclass(init=False)
class NotInitializable(DataClass):

    first_name: str
    last_name: str

    def __post_init__(self):
        ...  # private method called after initialization


# ── Slots ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlottedDataClass:

    """Only use slots when you know what you're doing."""

    status: str = "Pending"


# ─── Structural Pattern Matching ─────────────────────────────────────────────

def match_condition(condition: bool | None) -> str:
    match condition:
        case True:
            result = "True"
        case False:
            result = "False"
        case None:
            result = "None"
        case _:
            result = "Unknown"
    return result


def switch_case(a: int, b: int) -> str:
    match (a, b):
        case [1, 2]:
            result = "match case 1, 2"
        case [1, 