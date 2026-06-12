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
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5



# ── Slots ─────────────────────────────────────────────────────────────────────

class MyDataClassWithSlots():
    __slots__ = ("foo", "bar")

    def __init__(self, foo: int, bar: str) -> None:
        self.foo = foo
        self.bar = bar


def main() -> None:

    print(f"Point zero distance to itself is: {Point(0, 0).distance(Point(0, 0))}")

    my_point = Point(3.4, 6.789)
    print(my_point.distance(Point(10, 10)))

    print("\n\n\n")


    # ── Generics and type hints ─────────────────────────────────────────────────

    class Vector(Generic[K]):
        def __init__(self, origin_x: K, origin_y: K, destination_x: K, destination_y: K) -> None:
            self.origin = Point(origin_x, origin_y)
            self.destination = Point(destination_x, destination_y)


    # ── Structural Pattern Matching ─────────────────────────────────────────────

    def parse_json(json_str: str) -> dict[str, Any]:
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(e.msg) from e
        else:
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected a dictionary but got {type(parsed)} instead.")
            return parsed


    data = """
        {
            "name": "John Doe",
            "age": 43,
            "phones": [
                "+44 1234567",
                "+44 2345678"
            ]
        }
    """

    result = parse_json(data)
    assert result["name"] == "John Doe"
    assert result.get("occupation") is None
    assert result["age"] == 43
    assert all(isinstance(phone, str) for phone in result["phones"])
    assert isinstance(result, dict)

    # ── Walrus Operator ────────────────────────────────────────────────────────

    with open("/etc/passwd", mode="r") as file:
        while line := file.readline():
            print(line.strip())

    # ── Exception Groups ────────────────────────────────────────────────────────

    class CustomException(Exception):
        pass


    exc_list_1 = [CustomException(), CustomException()]
    exc_list_2 = [CustomException()]

    exc_group = ExceptionGroup(
        f"{len(exc_list_1)} exceptions have occurred.",
        value=exc_list_1,
    )

    exc_group.add_exception(CustomException())
    exc_group.add_exceptions(exc_list_2)

    exc_group2 = ExceptionGroup(
        f"{len(exc_list_1)+len(exc_list_2)} exceptions have occurred.",
        value=[*exc_list_1, *exc_list_2],
    )
    assert exc_group == exc_group2
    assert exc_group[0].isinstance(exc_group2[0])

    # ── Data Classes ────────────────────────────────────────────────────────────


    @dataclasses.dataclass()
    class Person:
        name: str
        age: int
        gender: Optional[str] = None


    p: Person = Person(name="Alice", age=30)
    assert p.name == "Alice"
    assert p.age == 30
    assert p.gender is None

    # ── Async/Await ────────────────────────────────────────────────────────────

    async def some_async_function() -> str:
        await asyncio.sleep(random.uniform(1, 5))
        return "Hello World"


    async def execute_some_task() -> None:
        result = await some_async_function()
        print(result)



# ── Imports ───────────────────────────────────────────────────────────────────

from __future__ import annotations

import abc, asyncio, concurrent.futures, dataclasses, datetime, decimal, functools, itertools, logging, math, os, pathlib, queue, random, re,    runtime_checkable,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from typing_extensions import Self

    from .types import *
    from .utils import *


# ── Utilities ─────────────────────────────────────────────────────────────────

def is_empty(obj: object) -> bool:
    if obj is None or len(obj) == 0:
        return True
    elif hasattr(obj, "__getitem__"):
        for item in obj:
            return False
        return True