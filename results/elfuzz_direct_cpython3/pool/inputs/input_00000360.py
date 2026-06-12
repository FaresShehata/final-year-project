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
class Runnable(Protocol): ...
Runnable.__doc__ += " + 'async def run()'"


# ─── Asyncio & generators ──────────────────────────────────────────────────

def gen_fn() -> Generator[int, None, None]:
    """generator function"""
    for i in range(5):
        yield i**2
gen_fn().__next__()

async def async_gen_fn() -> AsyncGenerator[int, None]:
    """asynchronous generator function"""
    for i in range(5):
        await asyncio.sleep(i)
        yield i**2
async_gen_fn().__anext__()

async def async_generator_factory():
    """factory that returns an asynchronous generator"""
    while True:
        yield (i := random.randint(0, 9))
        await asyncio.sleep(0.5)


# ─── Dataclasses ────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Person:
    name: str
    age: int
    height: float = dataclasses.field(compare=False)

    def make_json_serializable(self) -> dict[str, object]:
        return {"name": self.name, "age": self.age}

    @classmethod
    def from_json_data(cls, data: dict[str, object]) -> Person:
        return cls(**data)

@dataclasses.dataclass(slots=True)
class PersonSlots(Person):
    pass
PersonSlots.from_json_data({"name": "John", "age": 30})


# ─── Slots ──────────────────────────────────────────────────────────────────

class Animal:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Animal):
            raise TypeError(f"can't compare {type(self)} and {type(other)} objects")
        return self.name == other.name

    def __hash__(self) -> int:
        return hash((self.name, type(self)))

cat = Animal(name="Whiskers")
dog = Animal(name="Fido")


# ─── Structural pattern matching ────────────────────────────────────────────

def show_age(person: Person):
    match person:
        case Person(age=0):
            print("person is a baby 🎂")
        case Person(age=range(0, 18)):
            print