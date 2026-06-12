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
        return key.lower() == value.lower()


class ByPrice(Filter[int, int]):
    def filter(self, key: int, value: int) -> bool:
        return key >= value


class ByCount(Filter[T, int]):
    _count: int

    def __init__(self, count: int) -> None:
        self._count = count

    def filter(self, key: T, value: int) -> bool:
        return value >= self._count


@overload
async def get_items_by_filter(filter_: Filter[K, V], iterable: Iterable[tuple[K, V]]) -> list[V]:
    ...


@overload
async def get_items_by_filter(filter_: Filter[K, V], iterable: AsyncIterable[tuple[K, V]]) -> list[V]:
    ...


async def get_items_by_filter(
    filter_: Filter[K, V],
    iterables: tuple[Union[Iterator[tuple[K, V]], AsyncIterable[tuple[K, V]]]]
) -> list[V]:
    results = []
    for item in iterables:
        results.extend([item] if isinstance(item, Iterable) else (yield from item))
    filtered_items = [item for item in results if filter_.filter(*item)]
    return filtered_items


async def main_get_items_by_filter():
    entries = [
        ("banana", 34),
        ("apple", 10),
        ("pear", 56),
        ("orange", 98),
        ("grapefruit", 17),
        ("peach", 87),
    ]
    banana_filter = ByName()
    apple_filter = ByPrice()

    items = await get_items_by_filter(banana_filter, entries)
    assert items == [("banana", 34)]

    items = await get_items_by_filter(apple_filter, entries)
    assert items == [("apple", 10)]


# ── Walrus Operator ────────────────────────────────────────────────────────────


async def do_something(delay: float) -> float:
    await asyncio.sleep(delay)
    return delay


async def main_walrus_operator():
    entries = {
        "first": await do_something(0.01),
        **{"second": await do_something(0.02)},
        "third": await do_something(0.03),
    }
