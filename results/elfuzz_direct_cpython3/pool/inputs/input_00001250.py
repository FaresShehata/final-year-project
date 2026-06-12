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

# ── Enums ───────────────────────────────────────────────────────────────────────


class Color(str, enum.Enum):
    RED: str = "red"
    BLUE: str = "blue"
    GREEN: str = "green"


@runtime_checkable
class Box(Protocol[K]):
    """A protocol for boxes (containers) with an element of type K."""

    def get(self) -> K:
        ...


# ── Data classes ────────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Person:
    id_: int
    name: str
    age: int | None

    @property
    def is_adult(self) -> bool:
        return self.age >= 18


@dataclasses.dataclass(slots=True)
class Position:
    x: float
    y: float
    z: float

    def as_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


# ── Generics ────────────────────────────────────────────────────────────────────


def generic_function(data_type: TypeVar) -> T:
    if isinstance(data_type, int):
        return data_type + 1
    elif isinstance(data_type, str):
        return f"{data_type}!"
    else:
        raise TypeError("unsupported data type passed in")


# ── Structural pattern matching ────────────────────────────────────────────────


def match_person(person: Person) -> None:
    match person:
        case Person(id_=id_, name=name, age=None):
            print(f"name: {name}, id: {id_}")
        case Person(id_=id_, name="John", age=age):
            print(f"name: John, id: {id_}")
        case Person(name="Jane", age=age):
            print(f"name: Jane, age: {age}")
        case _:
            print("unknown person")


match_person(Person(id_=1, name="Alice", age=30))
match_person(Person(id_=2, name="Bob"))


# ── Walrus operator ────────────────────────────────────────────────────────────


async def count_to_ten() -> None:
    i: int = 0
    while True:
        await asyncio.sleep(1)
        print(i := i + 1)
        if i > 9:
            break


count_to_ten()


# ──