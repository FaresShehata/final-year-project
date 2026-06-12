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

    def __str__(self) -> str:
        return f"priority{self.value}"


# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:

    first_name: str
    last_name : str | None = None

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name


# ── Generics ──────────────────────────────────────────────────────────────────

_T_co = TypeVar("_T_co", covariant=True)


@runtime_checkable
class SupportsCmpOp(Protocol[_T_co]):
    
    def __eq__(self, other: object) -> bool:
        ...

    def __lt__(self, other: object) -> bool:
        ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False)
class FizzbuzzNumber:
    

    value: int
    status : Status
    priority: Priority


# ── Contexts ──────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class Config:
    
    name       : str
    version    : int = 1.0
    description: str = ""

@dataclasses.dataclass
class ContextManagerConfig(Config):

    verbose : bool = True
    
    def __enter__(self):
        print(f"Entering context with {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        
        if exc_type is not None and isinstance(exc_value, Exception):
            print(f"Exiting context with error {exc_value.__class__.__name__}")
        elif self.verbose or (self.verbose == False and exc_type is None):
            print(f"Exiting context without errors")


ContextManagerConfig()


async def wait_until_done(task: Awaitable[T]) -> T:
    while True:
        try:
            return await task
        except asyncio.CancelledError:
            continue


# ── Classes that do nothing ───────────────────────────────────────────────────


class EmptyClass:

    def method1() -> None:
        pass

    def method2(a: str) -> str:
        return a


EmptyClass()

v_1 = EmptyClass.method1()
v_2 = EmptyClass().method2("foo bar baz")


# ── Abstract Base Classes ─────────────────────────────────────────────────────

class AbstractClass(Protocol):

    @classmethod
    def from_dict(cls, d: dict[str, list[int]]) -> AbstractClass:
        ...

    def to_dict

def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


