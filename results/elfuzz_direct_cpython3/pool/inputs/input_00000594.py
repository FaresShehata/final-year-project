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


# ─── Slots and Structural Pattern Matching ───────────────────────────────────

class Product:
    __slots__ = ("_id", "_price")

    @property
    def id(self) -> int:
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