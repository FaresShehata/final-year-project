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
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

if TYPE_CHECKING:
    from types import TracebackType


class Color(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    color: Color = dataclasses.field(compare=False)

    def greet(self):
        return f"{self.first_name} {self.last_name}, age {self.age}"


def _get_persons() -> List[Person]:
    persons: List[Person] = []

    for i in range(10_000):
        person = Person(
            first_name=f"first_{i}",
            last_name=f"last_{i}",
            age=random.randint(5, 98),
            color=Color(random.choice([c.value for c in Color])),
        )
        persons.append(person)

    return persons


async def _task_get_persons():
    """A coroutine that returns a list of Person instances."""
    persons = await asyncio.gather(*(_get_persons(),))
    return persons


# noinspection PyShadowingNames
async def main():
    print("hello world")

    start_time = time.time()

    persons: List[Person] = await _task_get_persons()
    print(time.time() - start_time)


# noinspection PyShadowingNames
async def main_async():
    """The same as the above function, but using an asynchronous context manager."""

    async with (await _task_get_persons()) as persons:
        print(len(persons))


async def _count_items(items: Iterable[int]) -> Dict[str, int]:
    count_dict = {"sum": sum(items), "len": len(items)}
    return count_dict


async def _add_two_numbers(a: int, b: int) -> int:
    return a + b


async def _test_coroutines():
    # Coroutines are not awaited by default. They are scheduled and run as soon as they become available.
    await _add_two_numbers(1, 2)

    # Asynchronous context managers.
    async with await _count_items(range(10)) as count_dict:
        print(count_dict)

    # To