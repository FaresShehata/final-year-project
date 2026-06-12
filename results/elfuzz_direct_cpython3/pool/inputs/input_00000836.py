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
class Comparable(Protocol[K]):
    """A protocol for classes that can be compared using `<` and `>`."""

    def __lt__(self, other: K) -> bool:
        ...

    def __gt__(self, other: K) -> bool:
        ...

    def __le__(self, other: K) -> bool:
        ...

    def __ge__(self, other: K) -> bool:
        ...


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Foo:
    id_: int
    name: str

    def some_method(self) -> str:
        return f"Hello, I'm ID {self.id_}"


@dataclasses.dataclass(slots=True, frozen=True)
class Bar:
    id_: int
    name: str

    def some_method(self) -> str:
        return f"Hello, I'm ID {self.id_}"


@dataclasses.dataclass(order=True)
class Baz:
    foo: Foo
    bar: Bar

    def some_method(self) -> str:
        return f"{self.foo.some_method()}, {self.bar.some_method()}"


# ── Generics ───────────────────────────────────────────────────────────────────

def a() -> T:
    return "abc"


def b(t: T) -> T:
    return t


def c(v: V) -> V:
    return v


def d(k: K) -> K:
    return k


def e(k: K, v: V) -> tuple[V, K]:
    return v, k


def f(k: K) -> V:
    return k[0]


def g(k: K) -> V:
    return k[-1]


def h(*args: V) -> tuple[V, ...]:
    return args


def i(arg: V) -> V:
    return arg


async def a() -> T:
    return "abc"


async def b(t: T) -> T:
    return t


async def c(v: V) -> V:
    return v


async def d(k: K) -> K:
    return k


async def e(k: K, v: V) -> tuple[V, K]:
    return v, k


async def f(k: K) -> V:
    return k[0]


async def g(k: K) -> V:
    return k[-1]


async def h(*
            # Otherwise, we need to copy all the values manually.
            result: list[T] = []
            cache_idx = 0
            while True:
                try:
                    result.append(next(self))
                    cache_idx += 1
                except StopIteration:
                    break

            return result[start:stop]
        else:
            return next(iter(self.__iter__), None)


@dataclasses.dataclass(frozen=True)
class Point:
    """
    An immutable point class with integer x and y coordinates.

    >>> p = Point(x=1, y=2)
    >>> p.x
    1
    >>> p.y
    2
    >>> p.z
    Traceback (most recent call last):
      ...
    AttributeError: 'Point' object has no attribute 'z'
    """

    x: int
    y: int

    @classmethod
    def from_json(cls, s: str) -> Point:
        return cls(**json.loads(s))

    def __post_init__(self) -> None:
        assert isinstance(self.x, int)
        assert isinstance