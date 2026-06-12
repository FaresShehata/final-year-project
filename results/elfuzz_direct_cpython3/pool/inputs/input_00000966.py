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


# ── Data classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Item(Generic[K]):
    priority: int
    value: K

    # noinspection PyUnresolvedReferences
    def __repr__(self):
        return f"Item({self.priority=!r}, {self.value})"


@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    address: Address
    phone_numbers: tuple[str]
    email_address: str = dataclasses.field(default="none@example.com", compare=False)


@dataclasses.dataclass(frozen=True, slots=True)
class Address:
    street_name: str
    house_number: str | None = None


# ── Generic types ────────────────────────────────────────────────────────────

class Array[T]:
    def __init__(self, values: list[T] | None = None):
        if values is None:
            values = []
        self.values = values

    def append(self, item: T):
        self.values.append(item)

    def pop(self) -> T:
        return self.values.pop()

    def items(self) -> Iterator[T]:
        yield from self.values

    def count(self, item: T) -> int:
        return self.values.count(item)


class Factory[G]:
    def __init__(self):
        self.generation = 0

    def create(self) -> G:
        self.generation += 1
        return G(self.generation)


# ── Async/await ─────────────────────────────────────────────────────────────

async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def main() -> None:
    for _ in range(3):
        print(await get_random_number())
        await sleep(1.0)


async def get_random_number() -> float:
    return random.random()


asyncio.run(main())


# ── Protocols ───────────────────────────────────────────────────────────────

P = TypeVar("P")


@runtime_checkable
class Iterable(P):
    ...  # pragma: no cover

@runtime_checkable
class Container(P):
    ...  # pragma: no cover

@runtime_checkable
class Sized(P):
    def __len__(self) -> int: ...
    ...  # pragma: no cover

@runtime_checkable
class Reversible(P):
    ...  # pragma: no cover

@runtime_checkable
class AsyncIterable(P):
    ...  # pragma: no cover

@runtime_checkable
class AsyncContainer(P):
    ...  # pragma: no cover

@runtime_checkable
class AsyncSized(P):
    def __len__(self) -> int: ...
    ...  # pragma: no cover

@runtime_checkable
class AsyncReversible(P):
    ...  # pragma: no cover

@runtime_checkable
class AsyncIterable(P):
    ...  # pragma: no cover


# ── Structural pattern matching ──────────────────────────────────────────────

def match(x: object) -> str:
    match x:
        case (int(), str()):
            return "Pair of an integer and a string!"
        case (str(), int()):
            return "Pair of a string and an integer!"
        case _:  # default case (otherwise raise TypeError!)
            return "I don't know what to do with this!"

assert match((42, "Hello")) == "Pair of an integer and a string!"
assert match(("Hello", 42)) == "Pair of a string and an integer!"
try:
    match(True)
except TypeError as e:
    assert str(e) == "'bool' object is not iterable"


# ── Walrus Operator ──────────────────────────────────────────────────────────

numbers = [random.randint(0, 9) for _ in range(1_000)]
result = sum(
    n ** 2 for n in numbers if (n := random.choice(numbers)) % 8 == 0
)
print(result)


# ── Typing Generics ──────────────────────────────────────────────────────────

factory = Factory[int]()
ints = [
    factory.create(),
    factory.create(),
    factory.create(),
]

for i in ints:
    print(i)

# ── Exception Group ──────────────────────────────────────────────────────────

with ExceptionGroup("Nested error") as group:
    try:
        raise KeyError("Foo")
    except IndexError as ex:
        group.add_exception_type(IndexError)
        raise LookupError() from ex

    try:
        raise ValueError("Bar")
    except ValueError as ex:
        group.add_exception_type(ValueError, "Oops!")
        raise TypeError() from ex

group.print_details()
for exc in group.exceptions:
    print(exc.args[0])