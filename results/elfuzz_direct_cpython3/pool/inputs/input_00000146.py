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
    COMPLETED = "completed"

@runtime_checkable
class HasStatus(Protocol[K]):
    status: Status

@runtime_checkable
class IsComplete(Protocol[K]):
    def is_complete(self) -> bool:
        ...

@runtime_checkable
class CanBeCompleted(Protocol[K]):
    @staticmethod
    def complete() -> K | None:
        ...

# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(eq=True)
class NameDataClass:
    name: str
    age: int
    hobbies: list[str]
    id: int = dataclasses.field(compare=False)

    def __repr__(self): return f"{self.__class__.__name__}({self.name}, {self.age})"

@dataclasses.dataclass(order=True)
class OrderedNameDataClass(NameDataClass):
    class Meta:
        ordering_fields: tuple[str, ...] = ("age", "hobbies")
    def __str__(self): return f"[{self.id}] {self.name}"

# ─── Structural Pattern Matching ────────────────────────────────────────────

def greet1(
    value: dict[str, object],
) -> None:
    if isinstance(value["type"], int):
        print(f"I'm a number {value['type']}")
    elif isinstance(value["type"], str):
        print(f"I'm a string '{value['type']}'")
    else:
        raise ValueError()

def greet2(
    value: dict[str, object],
) -> None:
    match value["type"]:
        case int():
            print(f"I'm an integer {value['type']}")
        case str():
            print(f"I'm a string '{value['type']}'")
        case _:
            raise ValueError()

def greet3(
    value: dict[str, object],
) -> None:
    match value["type"]:
        case int(x):
            print(f"I'm an integer {x}")
        case str(s):
            print(f"I'm a string {s}")
        case _:
            raise ValueError()

def greet4(
    value: dict[str, object],
) -> None:
    match value["type"]:
        case int(x):
            print(f"I'm an integer {x}")
        case str(y) as z:
            print(f"I'm a string {z}, {y}")
        case _:
            raise ValueError()

def greet5(
    value