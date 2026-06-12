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
from unittest.mock import Mock

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator, Iterable, Iterator, Mapping

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")


@runtime_checkable
class HasId(Protocol):
    id: int


@dataclasses.dataclass(frozen=True, slots=False)
class User:
    name: str
    age: int

    def __str__(self) -> str:
        return f"{self.name}({self.age})"


# this class should raise an error when trying to use __slots__
@dataclasses.dataclass(slots=True)
class UserWithSlots:
    name: str
    age: int

    def __post_init__(self):
        self.id_counter = self._get_id()

    @classmethod
    def _get_id(cls):
        cls.__slots__.append("__id")
        # 0 or positive integer
        cls.__slots__[cls.__slots__.__len__() - 1] = "__id"
        cls.__slots__.remove("name")
        cls.__slots__.remove("age")

        setattr(cls, "id", property(lambda _: cls.__slots__[cls.__slots__.__len__() - 1]))
        return 3456789


class DataStructures:
    """
    Simple tests for datastructures.
    """

    def test_dataclasses(self):
        user1 = User(name="John", age=30)
        user2 = dataclasses.replace(user1, name="Jane", age=25)

        assert user1 != user2

        print(user1 == user2)

    def test_slots(self):
        u1 = UserWithSlots("Alice", 30)
        u2 = dataclasses.replace(u1, name="Bob", age=35)

        print(u1)
        print(u2)


class ListsAndIterators:
    """
    Simple tests for lists and iterators.
    """

    def test_lists_iterators(self):
        mylist = [i * i for i in range(5)]
        it = iter(mylist)

        while True:
            try:
                print(next(it))
            except StopIteration:
                break

    def test_generators(self):
        def gen():
            yield 1
            yield 2
            yield 3

        g = gen()
        print(next(g))

    def test_aiter_and_anext(self):
        async def main():
            async for    return re.match(pattern, string) is not None


def identity(value: A) -> A:
    return value


def get_last_item(item_list: list[A]) -> A | None:
    return item_list[-1]


def map_with_index(items: Iterable[A]) -> Iterator[tuple[int, B]] | None:
    index = 0
    try:
        for item in items:
            yield index, item
            index += 1
    except StopIteration:
        pass


def reduce_by_key(
    items: Iterable[tuple[Any, B]],
