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


@dataclasses.dataclass
class Order(Generic[K], metaclass=ABCMeta):
    id_: K
    quantity: int
    product: Product

    @property
    def subtotal(self) -> int:
        return self.quantity * self.product.price


@dataclasses.dataclass(order=True, frozen=True)
class OrderPacked(Order[int]):
    packed_at: datetime.datetime | None = dataclasses.field(compare=False)


@dataclasses.dataclass(order=True, frozen=True)
class OrderShipped(Order[Packed]):
    shipped_at: datetime.datetime | None = dataclasses.field(compare=False)


@dataclasses.dataclass(order=True, frozen=True)
class OrderDelivered(Order[Shipped]):
    delivered_at: datetime.datetime | None = dataclasses.field(compare=False)


@dataclasses.dataclass
class Cart:
    products: list[Product] = dataclasses.field(default_factory=list)
    order_id: int = 1

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def checkout(self) -> OrderPacked:
        order = OrderPacked(
            self.order_id,
            len(self.products),
            Product.random(),
        )
        self.order_id += 1
        return order


def main() -> None:
    print("Hello World!")


if __name__ == "__main__":
    main()


# ── Higher-Order Functions ─────────────────────────────────────────────────────


async def factorial(n: int) -> int:
    fact = 1
    for i in range(2, n + 1):
        print(f"Calculate factorial({n}) -> {i}")
        await asyncio.sleep(random.random())
        fact *= i
    return fact


async def main_1() -> None:
    task_list = [
        asyncio.create_task(factorial(i)) for i in range(5)
    ]
    results = [await fut for fut in task_list]
    print(results)

# ──────────────────────────────────────────────────────────────────────────────


async def factorial_async(n: int) -> int:
    if n <= 1:
        return 1
    else:
        return n*await factorial_async(n-1)


async def main_2() ->