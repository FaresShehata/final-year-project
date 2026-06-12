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


@dataclasses.dataclass(order=True)
class FilesystemEntry(Generic[K]):
    """Represents a filesystem entry."""

    name: str
    path: K
    size: int = 1 << 31 - 1
    priority: Priority = Priority.NORMAL
    status: Status = Status.PENDING
    flags: Flag = Flag.RWX

    @property
    def readable(self) -> bool:
        return self.flags & Flag.READ != Flag.NONE


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int


@runtime_checkable
def _is_person(obj: object) -> obj is Person:
    ...


@overload
def make_person(first_name: str, last_name: str, age: int) -> Person:
    ...


@overload
def make_person(person: Person) -> Person:
    ...


def make_person(*args: object) -> Person:
    if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], str) \
            and isinstance(args[2], int):
        return Person(*args)
    elif len(args) == 1 and isinstance(args[0], Person):
        return args[0]
    else:
        raise TypeError(
            f"expected (first_name: str, last_name: str, age: int), or (Person), got ({args})"
        )


person_1 = make_person("John", "Doe", 42)
print(person_1.first_name)
assert person_1.age == 42

# ─── Slots ──────────────────────────────────────────────────────────────────


@dataclasses.dataclass(slots=True, frozen=True)
class PersonWithSlots:
    first_name: str
    last_name: str
    age: int


@dataclasses.dataclass(slots=True, frozen=False)
class PersonWithMutableSlots:
    first_name: str
    last_name: str
    age: int


pws = PersonWithMutableSlots("Jane", "Doe", 47)
try:
    pws.name = "Alice"
except AttributeError as e:
    print(e)  # AttributeError: can't set attribute

# ─── Structural Pattern Matching ─────────────────