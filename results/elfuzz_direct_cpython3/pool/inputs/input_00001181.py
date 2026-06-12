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
S = TypeVar("S")


class Direction(enum.Enum):
    North = "N"
    East = "E"
    South = "S"
    West = "W"


@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int


def move(point: Point, direction: Direction) -> Point:
    if direction == Direction.North:
        return Point(x=point.x, y=point.y + 1)
    elif direction == Direction.East:
        return Point(x=point.x + 1, y=point.y)
    elif direction == Direction.South:
        return Point(x=point.x, y=point.y - 1)
    elif direction == Direction.West:
        return Point(x=point.x - 1, y=point.y)


async def get_weather_forecast(seasong: str) -> float | None:
    print(f"Getting weather forecast for {seasong} season...")
    await asyncio.sleep(5)
    if seasong == "winter":
        return 3.4
    else:
        return None


class WeatherForecastProtocol(Protocol):
    def __init__(self, data: dict[str, str]) -> None:
        ...

    @property
    def temp(self) -> float | None:
        ...

    @property
    def season(self) -> str | None:
        ...


def find_season(data: dict[K, V] | list[V] | tuple[V], search_key: K) -> V | None:
    """Find a value in a dictionary or list by key."""
    try:
        return next(value for key, value in data.items() if key == search_key)
    except StopIteration:
        return None


def generate_random_data() -> dict[str, T]:
    return {
        "name": f"{random.choice(['John', 'Jane'])}_{random.randint(100, 999)}".replace(
            "_",
            "",
        ),
        "age": random.randint(18, 65),
        "height_feet": round(random.uniform(5.0, 7.0), ndigits=2),
        "weight_lbs": round(random.uniform(100.0, 300.0), ndigits=2),
    }


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / (