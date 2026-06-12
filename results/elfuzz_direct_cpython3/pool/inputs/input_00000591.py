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

# ── Data Classes ───────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Product:
    name: str
    price: int
    discount_rate: float = 1.0

    @property
    def final_price(self) -> int:
        return int(round(self.price * self.discount_rate))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name}, {self.final_price})>"


@dataclasses.dataclass(frozen=True)
class Order:
    id: str
    products: frozenset[Product]

    def total_cost(self) -> int:
        return sum(product.final_price for product in self.products)


def print_order(order: Order) -> None:
    print(
        f"Order #{order.id}:",
        ", ".join(repr(p) for p in order.products),
        "\nTotal cost:",
        order.total_cost(),
    )


# ── Generics ───────────────────────────────────────────────────────────────────


class Filter(Generic[K, V]):
    def filter(self, key: K, value: V) -> bool:
        raise NotImplementedError()


class ByName(Filter[str, str]):
    def filter(self, key: str, value: str) -> bool:
        return True


class ByPrice(Filter[int, int]):
    def filter(self, key: int, value: int) -> bool:
        return True


class BySize(Filter[float, float]):
    def filter(self, key: float, value: float) -> bool:
        return abs(key - value) < 0.05


def select_products(orders: list[Order], filters: list[Filter]) -> set[Product]:
    selected_products: set[Product] = set()
    for order in orders:
        for filter_ in filters:
            if not all(filter_.filter(k, v) for k, v in order.products):
                break
        else:
            selected_products.update(order.products)
    return selected_products


def select_products_fast(orders: list[Order], filters: list[Filter]) -> set[Product]:
    by_name = ByName()
    by_price = ByPrice()
    by_size = BySize()

    for filter_ in [by_name, by_price, by_size]:
        for order in orders:
            if any(not filter_.filter(k, v) for k, v in order.products):
                break
        else:
            return {
                product
                for order in orders
                for product in order.products
               