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
    x: int
    y: int

@dataclasses.dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

@dataclasses.dataclass(init=False, order=True)
class Student:
    name: str
    grade: int

    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade


# ── Slots ─────────────────────────────────────────────────────────────────────

class Person(dataclasses.DataClass):
    __slots__: ClassVar[list[str]] = ["name", "_age"]
    age: int

p = Person(name="John", age=36)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(subject: T, cases: dict[Tuple[object], V]) -> V:
    """Pattern matching for Python.

    Args:
      subject (Any): The value to be matched.
      cases (dict[tuple of object, V]): A dictionary mapping patterns to values.

    Returns:
       V: The corresponding value if a match is found.
    """
    for pattern, value in cases.items():
        if all(isinstance(x, type(y)) and x == y for x, y in zip(pattern, subject)):
            return value
    raise ValueError("No case matches")


@match
def example_match(something: int | str | list[int]):
    match something:
        case 42:
            print("The answer")
        case "hello":
            print("Greetings Earthling!")
        case [a]:
            print(a)
        case []:
            print("Nothing here.")
        case _:
            print("Unknown input.")

example_match([1, 2, 3])

# ── Walrus Operator ───────────────────────────────────────────────────────────

def match_with_walrus_operator(subject: T, cases: dict[Tuple[object], V]) -> V:
    """Pattern matching for Python with the walrus operator.

    Args:
      subject (Any): The value to be matched.
      cases (dict[tuple of object, V]): A dictionary mapping patterns to values.

    Returns:
       V: The corresponding value if a match is found.
    """
    for pattern, value in cases.items():
        if all((x := x) == y for x, y in zip(pattern, subject)):
            return value
    raise ValueError("No case matches")


@match_with_walrus_operator
def example_match_with_walrus_operator(something: int | str | list[int]):
    match something:
        case 42:
            print("The answer")
        case "hello":
            print("Greetings Earthling!")
        case [a]:
            print(a)
        case []:
            print("Nothing here.")
        case _:
            print("Unknown input.")

example_match_with_walrus_operator([1, 2, 3])
print(wl := True)

# ── Generics ──────────────────────────────────────────────────────────────────

async def gather(*aws: Awaitable[T], return_exceptions: bool = False) -> tuple[T, ...]:
    """Gather results from multiple awaitables.

    Args:
        aws (Awaitable[T]): An iterable or a single awaitable.
        return_exceptions (bool): Whether to include exceptions as well.

    Returns:
        tuple[T, ...]: A tuple containing the results or exceptions.
    """
    tasks = []
    rets = []
    for aw in aws:
        task = asyncio.ensure_future(aw)
        tasks.append(task)
        try:
            rets.append(await task.exception())
        except BaseException as exc:
            if not return_exceptions:
                continue
            rets.append(exc)
    return tuple(rets)

# ── Exception Groups ───────────────────────────────────────────────────────────

class NotFoundException(Exception):
    def __str__(self) -> str:
        return "Not Found"

def handle_exception_group(exceptions: ExceptionGroup) -> None:
    for exception in exceptions.exceptions:
        if isinstance(exception, NotFoundException):
            print("Item already exists.")
            return