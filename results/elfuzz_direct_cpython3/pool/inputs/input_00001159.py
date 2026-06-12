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
    def from_dict(cls, d: dict[str, object]) -> Self: ...


@runtime_checkable
class Sensitive(Protocol[K]):
    def sensitive(self, key: K) -> str: ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    height: float = 1.87

    def greet(self) -> None:
        print(f"Hello, I'm {self.name} and I'm {self.age} years old.")


@dataclasses.dataclass(slots=True)
class Student(Person):
    major: str


# ── Generics ───────────────────────────────────────────────────────────────────

def add(a: T, b: T) -> T:
    return a + b


@overload
def multiply(a: T, b: T) -> T: ...
@overload
def multiply(a: T, b: T, c: T) -> T: ...
@overload
def multiply(a: T, b: T, c: T, d: T) -> T: ...
def multiply(*args: T) -> T:
    return sum(args) * len(args)


@dataclasses.dataclass(eq=False)
class Book:
    title: str
    author: str
    pages: int

    def check_out(self) -> None:
        if self.pages > 500:
            raise ValueError("Book too thick!")


class Queue(Generic[T]):
    def __init__(self):
        self.queue: list[T] = []

    def enqueue(self, item: T) -> None:
        self.queue.append(item)
    
    def dequeue(self) -> T:
        return self.queue.pop(0)


# ── Walrus Operator ────────────────────────────────────────────────────────────

a = ("b", "c", "d").index("c") == -1 \
    or (print("not found"), False) \
    or True


# ── Structural Pattern Matching ────────────────────────────────────────────────

def get_user_info(user_id: int) -> tuple[int, str]:
    return user_id, f"user_{user_id}"

def do_something(user_id: int) -> None:
    match get_user_info(user_id):
        case _ as info if