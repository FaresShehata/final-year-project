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


@dataclasses.dataclass(frozen=True)
class Point(Generic[K, V]):
    k: K
    v: V


# ── Modules ───────────────────────────────────────────────────────────────────

import datetime
import logging
import os
import sys


# ── Logging ──────────────────────────────────────────────────────────────────

formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")

file_handler = logging.FileHandler(filename="log.txt", mode="w")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])


logger = logging.getLogger(__name__)


def logger_func(msg: str, *args: object, level: int = logging.INFO, **kwargs: object) -> None:
    logger.log(level=level, msg=msg, *args, **kwargs)


# ── Enums ─────────────────────────────────────────────────────────────────────

class Color(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


my_color = Color.RED.value
print(my_color)


for item in Color.__members__.items():
    print(item[1])

# ── Enumerating over the values of an Enum: O(n), O(1) ───────────────────────

COLORS = {
    Color.RED,
    Color.GREEN,
    Color.BLUE
}

color_list = [
    Color.RED.value,
    Color.GREEN.value,
    Color.BLUE.value
]


# ── Enumerating over the Enum members themselves: O(n), O(1) ──────────────────

COLORS_LIST = [
    Color.RED,
    Color.GREEN,
    Color.BLUE
]


# ── Collections ───────────────────────────────────────────────────────────────

random.seed(time.time())


def shuffle(items: list[T], seed: int) -> list[T]:
    items_copy = items.copy()
    random.shuffle(items_copy, random.Random(seed))
    return items_copy


def reverse(items: list[T]) -> list[T]:
    items_copy = items[:]
    items_copy.reverse()
    return items_copy


my_items = ["foo", "bar"]

reversed_items = reversed(my_items)

deq = deque()

deq.appendleft(my_items.pop())

sorted_items = sorted(my_items)


# ── Binary Search ────────────────────────────────────────────────────────────

    for value, result in patterns:
        if value == obj or (isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return None


def match_with_default(obj: K | None, default: V, patterns: tuple[tuple[K, V]]) -> V | None:
    for value, result in patterns:
        if value == obj or (value is not None and isinstance(value, type) and isinstance(obj, value)):
            return result
    else:
        return default


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def count_to_3() -> Iterator[int]:
    yield 1
    a := yield 2
    yield 3


async def main():
    async for i in count_to_3():
        await asyncio.sleep(.5)
        print(i)


asyncio.run(main())


a = b = c = d = e = f = g = h = i = j = k = l = m = n = o = p = q = r = s = t = u = v = w = x = y = z = []


# ── Generics ─────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
E = TypeVar("E", bound=Exception)  # base class of all exceptions

MyDict[str, int] = dict[str, int]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Container(Protocol[A]):
    """The `Container` protocol represents any container that supports adding elements."""

    def add(self, element: A) -> None:
        ...


class HashableProtol(Protocol[B]):
    """The `HashableProtol` protocol specifies that objects must be hashable."""

    def __hash__(self) -> int:
        ...


class ComparableProtol(Protocol[C]):
    """The `ComparableProtol` protocol defines methods required to compare two instances of the same class."""

    def __lt__(self, other: C) -> bool:
        ...

    def __le__(self, other: C) -> bool:
        ...

    def __gt__(self, other: C) -> bool:
        ...

    def __ge__(self, other: C) -> bool:
        ...


def process_elements(container: Container[A]) -> None:
    for element in container:
        process_element(element)


def find_duplicates(data: list[Any]) -> set[Any]:
    seen = set()

    for item in data:
        if item in seen:
            continue

        seen.add(item)

    return seen


def find_duplicates_v2(data: list[Any]) -> set[Any]:
    duplicates = set()

    for item in data:
        if item in data[data.index(item):]:
            duplicates.add(item)

    return duplicates


def find_duplicates_v3(data: list[Any]) -> set[Any]:
    seen = set()
    duplicate = set()

    for item in data:
        if item in seen:
            duplicate