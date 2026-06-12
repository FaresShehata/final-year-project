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


@runtime_checkable
class SupportsAdd(Protocol[K, V]):
    """Supports addition of K to V."""

    @overload
    def __add__(self: Self, other: int | float) -> Self: ...

    @overload
    def __add__(
        self: Self,
        other: tuple[int, ...] | list[int],
    ) -> tuple[K, *int]: ...

    @overload
    def __add__(
        self: Self,
        other: tuple[float, ...] | list[float],
    ) -> tuple[K, *float]: ...

    @overload
    def __add__(self: Self, other: str) -> str: ...

    def __add__(self, other): ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    email: str

    def greet(self) -> str:
        greeting = f"Hello, I am {self.name}."
        if self.age < 30:
            greeting += " I'm a young person."
        else:
            greeting += " I'm an adult."
        return greeting

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name=}, {self.age=}, {self.email=})"


@dataclasses.dataclass(frozen=False)
class Book:
    title: str
    author: str

    def __post_init__(self):

        # check that `author` is not empty
        assert self.author != "", \
            "Book must have an author."

        # sort the author's last name alphabetically
        author_parts = self.author.split()
        assert len(author_parts) == 2, \
            "Author must be two parts (first and last)."
        self.__dict__["_author"] = f"{author_parts[0]} {sorted(author_parts)[-1]}"

    @property
    def author(self) -> str:
        return self._author

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"


# ── Generics ──────────────────────────────────────────────────────────────────

def add_numbers(x: int | float, y: int | float) -> int | float:
    return x