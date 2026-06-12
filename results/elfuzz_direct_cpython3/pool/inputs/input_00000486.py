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


# ── Types ────────────────────────────────────────────────────────────────────


@runtime_checkable
class Traceback(Protocol):
    @property
    def filename(self) -> str: ...
    @property
    def line(self) -> int: ...
    @property
    def func(self) -> str: ...


def get_traceback(exc: BaseException) -> Traceback | None:
    tb = exc.__traceback__
    while tb is not None:
        try:
            if isinstance(tb.tb_frame.f_globals['__name__'], str):
                return tb.tb_frame.f_globals.copy().pop('__name__', '')
            break
        except AttributeError:
            pass
        tb = tb.tb_next
    return None


# ── Exceptions ────────────────────────────────────────────────────────────────


class MyError(Exception):
    """My error."""


class ErrorGroup(ExceptionGroup):
    """An exception group."""

    def __init__(
        self,
        base_exception: BaseException,
        *exceptions: BaseException,
        description: str = "",
    ) -> None:
        super().__init__(base_exception, exceptions)
        self.description = description


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True, slots=True)
class Person:
    name: str
    age: int

    def say_hello(self) -> str:
        return f"Hi. I'm {self.name}."


def person_factory(name: str, age: int) -> Person:
    return Person(name=name, age=age)


@dataclasses.dataclass(frozen=False)
class StockMarketInfo:
    price: float
    volume: int

    def calculate_moving_average(self, n: int) -> float:
        """Calculate moving average over the last `n` days."""
        prices = [self.price]
        for _ in range(n - 1):
            prices.append(prices[-1] + random.randint(-3, 3))
        return sum(prices[-n:]) / len(prices)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StockMarketInfo):
            return self.price == other.price and self.volume == other.volume
        return False


StockMarkets = dict[str, StockMarketInfo]


@dataclasses.dataclass(slots=True)
class Portfolio:
    stocks: StockMarkets

    def update_stocks(self, **stocks: StockMarketInfo) -> None:
        self.stocks.update(stocks)

    def all_prices(self) -> list[float]:
        return [
            stock.market_info.price
            for _, market_info in self.stocks.items()
            for stock in market_info.shares
        ]

    def best_stock_price(self) -> float | None:
        return max(self.all_prices()) if self.all_prices() else None