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
    
    def keys(self) -> set[str]: ...

    def items(self) -> list[tuple[str, any]]: ...


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int
    gender: str

    def display_info(self) -> None:
        print(
            f"Name: {self.name}, Age: {self.age}, Gender: {self.gender}"
        )

    @property
    def info(self) -> tuple[str, int, str]:
        return self.name, self.age, self.gender
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(map(repr, self.info))})"


@dataclasses.dataclass(frozen=True, eq=False)
class Person(User):
    height: float
    weight: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        
        for field_name in self._fields:
            value_a = getattr(self, field_name)
            value_b = getattr(other, field_name)
            if value_a != value_b:
                return False
        
        return True


# ─── Slots ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Point:
    x: float
    y: float


# ─── Structural Pattern Matching ─────────────────────────────────────────────

def validate_user(user: dict) -> User:
    user_type = type(user)
    fields = {
        "name": str,
        "age": int,
        "gender": str
    }

    def check_field(field_name: str) -> bool:
        return field_name in user and isinstance(user[field_name], fields[field_name])

    if all(check_field(field_name) for field_name in fields):
        return User(**user)

    raise ValueError(f"Invalid user format. Expected: {fields}. Got: {user_type}'")


def validate_person(person: dict) -> Person:
    person_type = type(person)
    fields = {
        "name": str,
        "age": int,
        "height": float,
        "weight": float,
        "gender": str
    }
    
    def check_field(field_name: str) -> bool:
        return field_name in person and isinstance(person[field_name], fields[field_name])
    
    if all(check_field(field_name) for field_name in fields):
        return Person(**person)

    raise ValueError(f"Invalid person format. Expected: {fields}. Got: {person_type}")


users_data = [
    {"name": "Alice", "age": 26, "gender": "female"},
    {"name": "Bob", "age": 42, "gender": "male"}
]

people_data = [
    {"name": "Cindy", "age": 17, "height": 168.5, "weight": 45.5, "gender": "female"},
    {"name": "David", "age": 34, "height": 180.2, "weight": 88.7, "gender": "male"}
]


for user_data in users_data:
    try:
        user = validate_user(user_data)
    except ValueError as e:
        print(e)
    else:
        user.display_info()

for person_data in people_data:
    try:
        person = validate_person(person_data)
    except ValueError as e:
        print(e)
    else:
        person.display_info()


# ─── Walrus Operator ─────────────────────────────────────────────────────────

        return self._id

    @property
    def price(self) -> float:
        return self._price

    def __init__(self, id_: int, price: float) -> None:
        self._id = id_
        self._price = price

    def __hash__(self) -> int:
        return hash((self.id, self.price))
    

def slot_product_factory() -> (int, float):
    """Generate a unique product ID."""

    global _product_id_generator

    _product_id_generator += 1
    return _product_id_generator, random.randint(100, 999)


_product_id_generator = 0


def generate_unique_products(count: int) -> list[Product]:
    return [
        Product(*slot_product_factory())
        for _ in range(count)
    ]


unique_products = generate_unique_products(30)

print(unique_products)


# ───