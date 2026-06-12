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
    def run(self) -> None: ...

@runtime_checkable
class Done(Protocol):
    def done(self) -> bool: ...

# ── Data Classes ───────────────────────────────────────────────────────────────

@d.dataclass(frozen=True)
class User:
    name: str
    age: int

@d.dataclass(frozen=True, slots=True)
class Person(User):
    address: str

def main_data_classes():
    user = User(name="John", age=30)
    person = Person(
        name=user.name, 
        age=user.age, 
        address="123 Main St."
    )
    
    print(user)
    print(person)


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=False)
class SlotUser:
    name: str
    age: int
    
@dataclasses.dataclass(slots=True)
class SlotsPerson(SlotUser):
    pass    

# ── Structural Pattern Matching ────────────────────────────────────────────────

@overload
def match(data: Literal[True]) -> None: ...
@overload
def match(data: int) -> None: ...
@match
def foo(data):
    if isinstance(data, int):
        print('int')
    elif isinstance(data, str):
        print('str')
    else:
        raise TypeError(type(data))

foo(True)
foo(1)
foo("a")
try:
    foo(object())
except TypeError as e:
    print(e.__cause__)


@overload
def match(data: Literal[True]) -> None: ...
@overload
def match(data: int) -> None: ...
@overload
def match(data: float) -> None: ...
@match
def foo(data):
    match data:  # type: ignore
        case True:
            print('bool')
        case int():
            print('int')
        case float():
            print('float')

foo(True)
foo(1)
foo(1.0)
try:
    foo(object())  # type: ignore
except TypeError as e:
    print(e.__cause__)

# ── Walrus Operator ───────────────────────────────────────────────────────────

async def f() -> None:
    while (i := random.randint(0, 10)) < 4:
        await asyncio.sleep(0.1)
        
f()

# ── Gener