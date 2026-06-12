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
    @classmethod
    def from_json(cls, json_str: str) -> T:
        """Parse a JSON string and turn it into an instance of this class."""
        ...

    @property
    def to_json(self) -> str:
        """Turn the object into a JSON string."""
        ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person(object):
    name: str
    age: int
    sex: str = "male"


@dataclasses.dataclass(order=True)
class Student(Person):
    grade: float

    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.grade})"


# ── Slots ──────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Planet(object):
    name: str
    size: float = 3.844e+6
    mass: float = 1.989e+30
    gravity: float = 1.622

    @property
    def density(self) -> float:
        volume = (4 / 3 * math.pi * self.size ** 3) / 1_000_000_000
        return self.mass / volume


# ── Structural pattern matching ────────────────────────────────────────────────

def get_status(status: Status) -> dict[str, str]:
    status_map = {
        Status.PENDING : {"message": "status not yet determined"},
        Status.RUNNING : {"message": "status running"},
        Status.SUCCESS : {"message": "success"},
        Status.FAILED   : {"message": "failure"},
        Status.CANCELLED: {"message": "cancelled"}
    }

    if status in status_map:
        return status_map[status]

    raise ValueError(f"Invalid status: {status}")


# ── Walrus operator ────────────────────────────────────────────────────────────

def find_persons_with_age(persons: list[Person], age: int) -> bool:
    for person in persons:
        if person.age == age:
            return True

    return False


async def main():
    ...


# ── Generics ───────────────────────────────────────────────────────────────────

def get_total(items: list[float]) -> float:
    total = 0
    for item in items:
        total += item

    return total


def get_average(items: list[float], divisor: float|int) -> float:
    return sum(items) / divisor


def filter_even_numbers(numbers: list[int]) -> list[int]:
    result = []
    for number in numbers:
        if number % 2 == 0:
            result.append(number)

    return result


def filter_positive_integers(numbers: list[int]) -> list[int]:
    return [number for number in numbers if isinstance(number, int) and number > 0]


# ── Exceptions ─────────────────────────────────────────────────────────────────

class NotEmptyError(Exception):
    message = "List must be non-empty."

    def __init__(self, message=None):
        super().__init__(message or self.message)


class CustomException(Exception):
    message = "Custom Error!"

    def __init__(self, message=None):
        assert message is None, "Cannot set custom message."
        super().__init__(f"{type(self).__name__}: {self.message}")


def handle_exceptions(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    ...
    def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise
    return wrapper


# ── Exception Groups ───────────────────────────────────────────────────────────

class GroupedExceptions(ExceptionGroup):
    def __init__(self, base_exception: BaseException, exceptions: list[BaseException]):
        super().__init__(
            description=f"Multiple errors occurred.",
            base_exception=base_exception,
            exceptions=exceptions
        )

    def add_explanation(self, explanation: str) -> None:
        ...

    def add_note(self, note: str) -> None:
        ...

    def add_tip(self, tip: str) -> None:
        ...


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ...

# EOF