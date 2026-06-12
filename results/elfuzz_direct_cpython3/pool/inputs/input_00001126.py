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


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)
    call_stack: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class Product:
    sku: str
    price: float
    weight_in_grams: float
    size_in_cm: tuple[float, float]


@dataclasses.dataclass
class OrderItem:
    product_id: str
    quantity: int
    amount: float
    total_discount: float
    price_per_unit: float
    price_with_discount: float


@dataclasses.dataclass(slots=True)
class ProductSummary:
    sku: str
    price: float
    discount_percent: float
    total_quantity: int
    total_amount: float
    avg_price: float
    max_discount: float
    min_max_ratio: float
    discount_percentage_on_min_max: float
    average_stock_level: float
    first_order_date: str
    last_order_date: str
    num_orders: int
    orders_with_zero_quantity: int
    monthly_orders: int
    first_week_of_month: int
    latest_week_of_month: int
    num_unique_customer_ids: int
    num_customers: int
    customer_with_most_orders: str
    customer_with_least_orders: str


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(x):
    if isinstance(x, int):
        print("x is an integer")
    elif isinstance(x, float):
        print("x is a float")


match(69)
match(1.0 / 3)
match(42 * "what?")

match(("this", "is", "a", "tuple")):
    case [first, second]:
        print(first, second)
    case ["this", *rest]:
        print(*rest)

match(("this", "is", "a", "tuple")):
    case [_, _, *other_elements]:
        print(other_elements)

match({"key": "value"}):
    case {"key": value}:
        print(value)
    case {"key": value, "another_key": another_value}:
        print(f"{value=} and {another_value=}")
    case {"key": key_part}:
        print(key_part)  # => "key"

match(None):
    case None:
        print("None!")
    case str():
        print("str!")


# ── Walrus Operator ─────────────────────────────────────────────────