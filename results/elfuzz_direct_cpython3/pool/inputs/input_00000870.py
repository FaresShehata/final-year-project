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

    def distance_to_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class NameAge:
    name: str
    age: int

    def greet(self) -> None:
        print(f"Hi I'm {self.name}, and I'm {self.age} years old!")

    @property
    def full_name(self) -> str:
        return f"{self.name.title()} {self.age}"


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_tuple(a: tuple[tuple[()], tuple[str]]):
    match a:
        case ("", b):
            ...
        case ("a", b):
            ...
        case (a, b):
            ...
        case other:
            raise ValueError(f"Unexpected value {other}")

match_tuple(("a", "b"))


def match_list(a: list[list[int], list[float]]) -> None:
    match a:
        case [x, y]:
            ...
        case [x, y]:
            ...
        case [x, y]:
            ...


def match_array(a: array.array[array.float64]) -> None:
    match a:
        case array.array(array.float64):
            ...


def match_enum(a: Status):  # OK
    match a:
        case Status.PENDING:
            ...
        case Status.RUNNING:
            ...
        case Status.SUCCESS:
            ...
        case Status.FAILED:
            ...
        case Status.CANCELLED:
            ...


def match_enum_with_unexpected_value(b: Status):  # Error
    match b:
        case Status.PENDING:
            ...
        case Status.RUNNING:
            ...
        case Status.SUCCESS:
            ...
        case Status.FAILED:
            ...
        case Status.CANCELLED:
            ...


def match_enum_pattern_matching(c: Status):  # OK
    match c:
        case Status.PENDING | Status.RUNNING:
            ...
        case Status.SUCCESS | Status.FAILED:
            ...
        case Status.CANCELLED:
            ...


def match_enum_if_else(d: Status):  # OK
    match d:
        case Status.PENDING:
            ...
        case Status.RUNNING:
            ...
        case Status.SUCCESS:
            ...
        case Status.FAILED:
            ...
        case Status.CANCELLED:
            ...


    return wrapper


def is_palindrome(s: str) -> bool:
    """Return whether the given string s is a palindrome."""

    l = len(s)
    if l % 2 == 0:
        # Odd number of letters.
        mid = l // 2
        return all([s[i] == s[l - i - 1] for i in range(mid)])
    else:
        # Even number of letters.
        mid = l // 2 + 1
        return all([s[i] == s[mid - i] for i in range(mid)])


@log_each
def test_is_palindrome() -> tuple[int, ...]:
    """Test is_palindrome()."""

    results = []
    for length in range(1, 51):
        n_tests = 5 * pow(length, 4)
        count = 0
        for _ in range(n_tests):
            s = "".join(secrets.choice(string.ascii_lowercase) for _ in range(length))
            if is_palindrome(s):
                count += 1
        count /= n_tests
        results.append(count)
    return tuple(results)


# ── NamedTuple ───────────────────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    """Return whether the given integer n is prime."""

    assert n >= 2
    if n == 2 or n == 3:
        return True

    d = 2