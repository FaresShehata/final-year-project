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


@dataclasses.dataclass(eq=True, order=True)
class Student:
    name: str
    age: int
    grades: list[float]

    def average_grade(self) -> float:
        return sum(self.grades) / len(self.grades)


@dataclasses.dataclass(slots=True)
class Person:
    """Class with private attribute."""

    _name: str

    def get_name(self) -> str:
        return self._name.upper() if self._name else ""

    def set_name(self, new_name: str) -> None:
        self._name = new_name[:255]

    def __repr__(self) -> str:
        return f"<Person(name={self.get_name()}, ...>"

    def __str__(self) -> str:
        return f"Name: {self.get_name()}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotObject(object):
    __slots__ = ["_x", "_y"]

    def __init__(self, x: int, y: int) -> None:
        self.set(x, y)

    def set(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return not (self == other)


class NonSlotObject(object):
    __dict__: dict[str, Any]

    def __init__(self, x: int, y: int) -> None:
        self._set(x, y)

    def _set(self, x: int, y: int) -> None:
        self.__dict__["_x"] = x
        self.__dict__["_y"] = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NonSlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, NonSlotObject):
            return NotImplemented
        return not (self == other)


# ─