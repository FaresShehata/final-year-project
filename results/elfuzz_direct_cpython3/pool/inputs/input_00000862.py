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
    A = 1 << 0  # bitfield flag type
    B = 1 << 1  # bitfield flag type
    C = 1 << 2  # bitfield flag type

    D = A | C  # compound assignment of flags
    E = (C | B) - C  # subtraction and bitwise complement

    @classmethod
    def from_hex(cls: type[Flag], hexstr: str) -> Flag:
        """Create flags from hexadecimal string."""
        bits = int(hexstr.lstrip('0x'), base=16)
        return cls(bits)

@runtime_checkable
class IterableWithIndex(Protocol[K, V]):  
    def __iter__(self) -> Iterator[V]:
        ...

    def __getitem__(self, index: K) -> V:
        ...  


@dataclasses.dataclass(frozen=True, slots=True)
class Item:
    id: int
    name: str
    price: float
    quantity: int
    total_price: float
  
    def __post_init__(self):            
        if not isinstance(self.id, int) or not isinstance(self.name, str)\
                or not isinstance(self.price, float)\
                or not isinstance(self.quantity, int)\
                or not isinstance(self.total_price, float):
            raise ValueError(
                f"Invalid types for Item attributes. Expected integers for 'id', "
                f"strings for 'name' and 'price', and floats for 'quantity' and 'total_price'."
            )

@runtime_checkable
class DataClassItem(Protocol[K, V]):
    item_id: int
    item_name: str
    item_price: float
    item_quantity: int
    item_total_price: float


def get_items() -> tuple[int, str, float, int, float]:  
    return 42, "Apple", 3.99, 10, 39.80


def process_items(items: list[DataClassItem]) -> None:
    sum_of_prices = sum(item.item_total_price for item in items)
    avg_item_price = sum_of_prices / len(items)
    print(avg_item_price)


async def main() -> None:
    items: list[DataClassItem] = []
    
    for)

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
    A = 1 << 0  # bitfield flag type
    B = 1 << 1  # bitfield flag type
    C = 1 << 2  # bitfield flag type

    D = A | C  # compound assignment of flags
    E = (C | B) - C  # subtraction and bitwise complement

    @classmethod
    def from_hex(cls: type[Flag], hexstr: str) -> Flag:
        """Create flags from hexadecimal string."""
        bits = int(hexstr.lstrip('0x'), base=16)
        return cls(bits)


@runtime_checkable
class IterableWithIndex(Protocol[K, V]):  
    def __iter__(self) -> Iterator[V]:
        ...

    def __getitem__(self, index: K) -> V:
        ...  


