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
    email: str
    phone_number: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    birth_date: datetime.date
    favorite_colors: Optional[Set[str]] = None
    pets: Optional[List["Pet"]] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None


@dataclasses.dataclass(frozen=True)
class Pet:
    name: str
    type: str
    age: int
    owner: Person
    color: str
    breed: Optional[str] = None
    weight_kg: float = 1.0


def get_person() -> Person:
    return Person(
        first_name="John",
        last_name="Doe",
        age=42,
        email="john.doe@example.com",
        phone_number="555-1234",
        address="123 Main St.",
        city="Anytown",
        state="CA",
        zip_code="12345",
        country="USA",
        birth_date=datetime.date(1978, 6, 1),
        favorite_colors=None,
        pets=[],
        job_title="Software Engineer",
        company="Example Inc.",
        salary=50_000.0,
    )


async def main():
    print("Hello, World!")


re.compile("foo")


class Node(Generic[T]):
    """A node in a singly linked list."""

    next_node: Optional[Node[T]] = None
    value: T

    def __init__(self, value: T):
        self.value = value


# class HeapHeap(Generic[T]):
#     min_heap: List[T]
#     max_heap: List[T]

#     def __init__(self):
#         self.min_heap = []
#         self.max_heap = []

#     def add(self, element: T):
#         if len(self.min_heap) == 0 and len(self.max_heap) == 0:
#             self.min_heap.append(element)
#         else:
#             # TODO: Implement this method.
#             pass

#     def remove_min(self) -> Optional[T]:
#         # TODO: Implement this method.
#         ...

#     def remove_max