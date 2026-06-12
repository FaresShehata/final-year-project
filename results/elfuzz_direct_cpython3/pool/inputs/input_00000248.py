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
    def from_dict(cls, d: dict): ...
        

def serialise(obj: object, *, cls=Serialisable) -> str:
    if isinstance(obj, classmethod):
        obj = obj.__get__(None)
    elif not isinstance(obj, cls):
        raise TypeError(f"{obj} must be an instance of {cls}")
    
    return json.dumps(obj.to_dict())


def deserialise(s: str, *, cls=Serialisable) -> object:
    return cls.from_dict(json.loads(s))


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False)
class MyClass:
    id: int
    name: str
    age: int = -1
    
    def get_name(self) -> str:
        return self.name
    
    def _is_valid_id(self) -> bool:
        return self.id >= 0
    

class MySecondClass:
    def __init__(self, a: int):
        self.a = a
        
    def get_a(self) -> int:
        return self.a
    
    
# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    __slots__ = ["name", "_age"]
    
    def __init__(self, name: str, age: int):
        self.name = name
        self._age = age
    
    @property
    def age(self) -> int:
        return self._age
    
    
# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person, *, default=None) -> None:
    match person:
        case Person(name="Alice"):
            print("It's Alice!")
        case Person(age=30):
            print("They are 30 years old.")
        case Person():
            print("I don't know who this is.")
        case default:
            print(default)


# ── Walrus Operator ───────────────────────────────────────────────────────────

def find_index(lst: list[int], x: int) -> int:
    for i, v in enumerate(lst):
        if v == x:
            return i
    return -1


def find_index_walrus(lst: list[int], x: int) -> int:
    for i, v := enumerate(lst):
        if v == x:
            return i
    return -1


# ── Generics ───────────────────────────────────────────────────────────────────

class SortedList(G    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

