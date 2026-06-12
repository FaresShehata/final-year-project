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
    A = 1
    B = 2


# ── Data structures ───────────────────────────────────────────────────────────

@runtime_checkable
class Sortable(Protocol[K]):
    """Sortable protocol.

    This class defines the contract for classes that can be sorted.
    """

    @classmethod
    def _compare(cls, a: K, b: K) -> int:
        raise NotImplementedError()


def insertionsort(array: list[K], *, compare: Callable[[K, K], int] | None = None) -> None:
    """Insertion sort algorithm."""
    if compare is None:
        compare = Sortable._compare
    n = len(array)
    for i in range(1, n):
        key = array[i]
        j = i - 1
        while j >= 0 and compare(key, array[j]) < 0:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key


@dataclasses.dataclass(frozen=True)
class Item():
    name: str
    weight: float
    value: int

colors = [
    ("red",   0.5),
    ("blue",  0.4),
    ("green", 0.3),
    ("purple", 0.2),
    ("yellow", 0.1),
]


class Color(Sortable["Item"]):

    def __init__(self, **kwargs) -> None:
        super().__setattr__("weight", kwargs["weight"])
        super().__setattr__("value", kwargs["value"])

    def __repr__(self) -> str:
        return f"{self.name}: {self.weight:.2f}, {self.value}"

    def __lt__(self, other: Color) -> bool:
        return self.weight < other.weight


insertionsort(colors)


# ── Generics and protocols ───────────────────────────────────────────────────

class Comparable(Generic[T]):
    ...


# ── Asyncio and concurrency ──────────────────────────────────────────────────

async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def generate_numbers() -> Iterator[int]:
    print("\n[GENERATE NUMBERS]")
    for i in range(6):
        yield i
        await sleep(i * 0.2)


async def add(a: int, b: int) -> int:
    print("[ADD]")
    await sleep(3)
    return a + b


async def multiply(a: int, b: int) -> int:
    print("[MULTIPLY]")
    await sleep(4)
    return a * b


async def divide(a: int, b: int) -> float:
    print("[DIVIDE]")
    await sleep(7)
    return a / b


async def main() -> None:
    numbers = []
    try:
        for number in generate_numbers():
            numbers.append(number)
            await sleep(1)
    except KeyboardInterrupt as e:
        print("\nKeyboardInterrupt received.")
    else:
        del numbers[-1]

    result = await asyncio.gather(
        add(numbers[0], numbers[1]),
        multiply(numbers[1], numbers[2]),
        divide(numbers[2], numbers[3])
    )

    print(result)


asyncio.run(main())


# ── Exceptions & exceptions groups ───────────────────────────────────────────

class InvalidInput(Exception):
    ...


class NotEnoughData(Exception):
    ...


async def process_data(data: dict[str, str]) -> tuple[list[str], int]:
    processed_data = []
    total_length = 0
    for key, value in data.items():
        if not isinstance(value, str):
            raise InvalidInput
        processed_data.append(key.upper())
        total_length += len(value)
        if total_length > 1_000_000:
            raise NotEnoughData()
    return (processed_data, total_length)


async def main() -> None:
    try:
        data = {"a": "b", "c": "d"}
        processed_data, total_length = await process_data(data)
    except InvalidInput:
        print("Invalid input detected.")
    except NotEnoughData:
        print("Not enough data to continue processing.")
    else:
        print(processed_data)
        print(total_length)


asyncio.run(main())

# ── Walrus Operator ──────────────────────────────────────────────────────────

name = "John"
age = 30
is_student = True

match_name = name := "Jane"  # assign match_name with the value of name
print(match_name)
print(name == match_name)

if age := 31:
    print(age == 31)

if is_student := False:
    print(is_student == False)

while (line := input()) != "":
    print(line.capitalize())

if (username := input("Enter username: ")) != "":
    print(f"Welcome back, {username}!")

match_name = name := "Jane"  # assign match_name with the value of name
match_value = value := 42  # assign match_value with the value of value
print(match_name)
print(match_value)

try:
    value = int(input("Enter an integer: "))
except ValueError as err:
    print(err)
    exit(1)
print(value)


# ── Structural Pattern Matching ──────────────────────────────────────────────

user_input = {
    "id": 1,
    "name": "Alice",
}

match user_input:
    case {"id": id_, "name": name}:
       print(f"id: {id_}, name: {name}")


match user_input:
    case {"id": id_, "name": name} if id_ % 2 == 0except NameError:
    pass
else:
    t = {
        "hello": "world",
    }

thing = {
    "hello": "world",
}
try:
    thing.update({"world": "foo"})
except AttributeError:
    pass
else:
