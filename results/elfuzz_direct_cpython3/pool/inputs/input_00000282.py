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


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Account:
    """Account class represents a bank account. It has an ID and balance."""

    id_: int
    balance: float

    @property
    def address(self) -> str:
        """Returns the account's address."""
        raise NotImplementedError()

    @classmethod
    def from_json(cls, value: dict[str, object]) -> Account:
        """Creates an instance of this class by deserializing from JSON."""
        if not isinstance(value["id"], int):
            raise TypeError("Invalid type for 'id': expected int.")
        if not isinstance(value["balance"], (int, float)):
            raise TypeError("Invalid type for 'balance': expected int or float.")
        return cls(id_=value["id"], balance=value["balance"])

    def to_json(self) -> dict[str, object]:
        """Serializes this instance into a JSON-serializable dictionary."""
        return {
            "id": self.id_,
            "balance": self.balance
        }


@dataclasses.dataclass(frozen=True)
class Order:
    """Order class represents a purchase order with attributes like product, quantity, price per unit, and shipping cost."""

    product: str
    quantity: int
    price_per_unit: float
    shipping_cost: float

    @staticmethod
    def create(product_name: str, quantity: int, price_per_unit: float, shipping_cost: float) -> Order:
        """Static method creates a new instance of the Order class with specified parameters."""
        return Order(product=product_name, quantity=quantity, price_per_unit=price_per_unit, shipping_cost=shipping_cost)

    @property
    def total_amount(self) -> float:
        """Calculates the total amount of the order based on quantity, price per unit, and shipping cost."""
        return self.quantity * self.price_per_unit + self.shipping_cost

    @classmethod
    def from_order_dict(cls, order_dict: dict[str, object]) -> Order:
        """Constructs an Order instance from a dictionary representation of an order."""
        if not isinstance(order_dict.get('product', ''), str):
            raise TypeError("Invalid type for 'product'")
        if not isinstance(order_dict.get('quantity', 0), int):
            raise TypeError("Invalid type for 'quantity'")
        if not isinstance(order_dict.get