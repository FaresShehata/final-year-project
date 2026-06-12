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


@runtime_checkable
class IterableWithIndex(Generic[K, V], Protocol):
    """
    A sequence-like protocol with an additional index attribute so we can iterate over the items in parallel.

    Note: This is an example only - there are better ways to do this.
    """

    def __iter__(self) -> Iterator[Tuple[V, K]]:
        ...

    def __getitem__(self, i: K) -> V:
        ...

    def __len__(self) -> int:
        ...

    @property
    def index(self) -> Sequence[int]:
        ...

# ─── Async/Await ─────────────────────────────────────────────────────────────-

async def forever():
    while True:
        await asyncio.sleep(random.uniform(1, 5))
        print(time.perf_counter())


# ─── Coroutines ───────────────────────────────────────────────────────────────

async def add(x: int, y: int) -> int:
    return x + y

async def multiply(x: int, y: int) -> int:
    return x * y

async def subtract(x: int, y: int) -> int:
    return x - y


# ─── Protocols ────────────────────────────────────────────────────────────────

class Item(object):

    id: int = 1

    @classmethod
    def generate_id(cls) -> int:
        return cls.id

    def get_title(self) -> str:
        raise NotImplementedError()


class Book(Item):

    title: str = ""
    author: str = ""


class Person:

    first_name: str = ""
    last_name: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Customer(Person):

    def __str__(self) -> str:
        return self.full_name


class User(Person):

    def __repr__(self) -> str:
        return f"<User {self.full_name}>"

    @classmethod
    def from_string(cls, user_str: str) -> User:
        first, last = user_str.split()
        return cls(first=first, last=last)

    @staticmethod
    def get_user(user_str: str) -> User:
        ...
    
    @classmethod
    def find_all_users(cls, user_ids: list[int]) -> list[User]:

        users = []
        for user_id in user_ids:
            user = cls.get_user(str(user_id))

        return users


# ─── Data Classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float


PointT = TypeVar("PointT", bound="Point")

def distance(p1: Point, p2: Point) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** 0.5



# ─── Slots ────────────────────────────────────────────────────────────────────

class Animal(metaclass=ABCMeta):
    _species: str

    def __new__(cls, species: str):
        instance = super().__new__(cls)
        instance._species = species
        return instance

    @abstractmethod
    def sound(self) -> str:
        ...

    @property
    def species(self) -> str:
        return self._species

    @abstractmethod
    def eat(self, food: str) -> str:
        ...


class Dog(Animal):
    def sound(self) -> str:
        return "woof!"

    def eat(self, food: str) -> str:
        return f"{self.species} eats {food}."


class Cat(Animal):
    def sound(self) -> str:
        return 'meow'

    def eat(self, food: str) -> str:
        return f'{self.species} eats {food}'


# ─── Structural Pattern Matching ──────────────────────────────────────────────

def match_example(item: Union[Item, str]) -> None:
    match item:
        case Book(title=title, author=author        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

