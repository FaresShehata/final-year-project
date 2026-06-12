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
    def from_json(cls: type[T], s: str) -> T:
        ...

    def to_json(self) -> str:
        ...


# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int

@dataclasses.dataclass(frozen=True)
class Student(Person):
    school: str
    grade: int

@dataclasses.dataclass(frozen=True)
class Instructor(Person):
    department: str
    years_experience: int


def show_person(person: Person) -> None:
    print(
        f"{person.first_name} {person.last_name}, "
        f"age={person.age}"
    )


show_person(Student('Bob', 'Jones', 42, 'MIT', 9))
show_person(Instructor('Alice', 'Smith', 38, 'CS', 12))


# ───────────────────────────────────────────────────────────────────────────────

Person.__annotations__['first_name']


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True, frozen=False)
class Person:
    first_name: str
    last_name: str
    age: int

def show_person(person: Person) -> None:
    print(
        f"{person.first_name} {person.last_name}, "
        f"age={person.age}"
    )

show_person(Person(first_name='Bob', last_name='Jones', age=42))

# TypeError: Can't set attribute 'last_name'

try:
    person.last_name = 'Doe'
except AttributeError as e:
    print(e)


# ─── Structural Pattern Matching ──────────────────────────────────────────────

a_match = {'type': 'Ok', 'value': 1}
b_match = {'type': 'Err', 'error': 'No such file'}
c_match = {'type': 'Ok', 'value': 'Hello'}

match a_match:
    case {'type': 'Ok', 'value': 1}:
        print('ok')
    case _:
        print('nothing')

match b_match:
    case {'type': 'Ok'}:
        print('nothing')
    case {'type': 'Err', 'error': 'Something'}:
        print('error something')
    case {'type':