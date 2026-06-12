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


@dataclasses.dataclass(frozen=True, kw_only=True)
class Employee(dataclasses.DataclassMixin):
    emp_no: int
    birth_date: str
    first_name: str
    last_name: str

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class EmployeeDict(dict[str, str]):
    _slots = ("emp_no", "birth_date", "first_name", "last_name")


# ── Structural pattern matching ────────────────────────────────────────────────

def parse_html(html_str: str | None) -> dict | None:

    if html_str is None or not isinstance(html_str, str):
        return None

    try:
        tag_matcher = re.compile(r"<([a-z]+)>.*</\1>")
    except TypeError as e:
        print(e)
        return None

    tags = list(tag_matcher.findall(html_str))
    if len(tags) != 3:
        return None

    if tags[0] == "html" and tags[-1] == "body":
        return {"title": tags[1], "headings": [tags[2]]}

    return None


# ── Walrus ────────────────────────────────────────────────────────────────────

async def coro() -> int:
    value = await get_value()
    return value


async def main():
    result = await coro()


# ── Generics ──────────────────────────────────────────────────────────────────

class DictionaryWrapper(Generic[K, V]):

    def __init__(self, dictionary: dict[K, V]):
        self._dictionary = dictionary

    def key_by_value(self, value: V) -> K | None:
        for k, v in self._dictionary.items():
            if v == value:
                return k
        return None


# ── Exception Groups ──────────────────────────────────────────────────────────

class JSONDecodeError(Exception):

    message: str

    def __init__(self, msg: str, pos: int, line: int, column: int):
        super().__init__()
        self.message = msg
        self.pos = pos
        self.line = line
        self.column = column


class ErrorCategory(enum.Enum):
    BAD_REQUEST = "