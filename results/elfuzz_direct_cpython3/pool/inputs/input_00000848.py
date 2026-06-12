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
class Animal(enum.Enum):
    COW = "Cow"
    DOG = "Dog"
    HAMSTER = "Hamster"

    @classmethod
    def names(cls) -> list[str]:
        return [i.value for i in cls]

    def __str__(self) -> str:
        return self.name


class Feline(Animal):
    CAT = "Cat"


@runtime_checkable
class Document(Protocol[T]):
    content: T

    def get_content(self) -> T:
        ...


# ── Dataclasses ──────────────────────────────────────────────────────────────
@dataclasses.dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str | None = None
    age: int | None = None
    active: bool = True
    created_at: float | None = None
    is_admin: bool = False

    def set_email(self, email: str) -> None:
        self.email = email

    def set_age(self, age: int) -> None:
        if age < 18 or age > 65:
            raise ValueError("Age must be between 18 and 65.")
        self.age = age

    def get_active_users_count(self) -> int:
        return sum(
            1 for user in users.values() if user.active == True
        )  # noqa E741


users: dict[int, User] = {
    1: User(id=1, name="Alice", email="alice@example.com"),
    2: User(id=2, name="Bob", email=None),
    3: User(id=3, name="Charlie", age=30),
}


@dataclasses.dataclass(frozen=False)
class Rectangle:
    x: float
    y: float
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


rects: list[Rectangle] = [
    Rectangle(x=-1.0, y=0.0, width=10.0, height=5.0),
    Rectangle(x=0.0, y=-2.0, width=7.0, height=3.0),
]


@dataclasses.dataclass()
class Point:
    x: float
