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
    z: float = 0.0  # default value for keyword argument

    def distance_to_origin(self) -> float:
        """Return the Euclidean distance of a point (x,y,z) to the origin (0,0,0)."""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def magnitude(self) -> float:
        """Return the magnitude or length of a vector."""
        return self.distance_to_origin()

    def dot_product(self, other: Point) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross_product(self, other: Point) -> Point:
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, z={self.z})"


@dataclasses.dataclass(frozen=True, order=False)
class LineSegment(Generic[K]):
    start: K
    end: K
    delta_x: float
    delta_y: float
    delta_z: float = 0.0

    def __post_init__(self):
        assert self.delta_x != 0 or self.delta_y != 0 or self.delta_z != 0, \
               "Line segment must have non-zero direction."

    def _get_step(self, k: K) -> tuple[float, float]:
        if isinstance(k, int):
            return self.delta_x // abs(self.delta_x), self.delta_y // abs(self.delta_y)
        else:
            return self.delta_x / abs(self.delta_x), self.delta_y / abs(self.delta_y)

    def get_steps(self) -> list[tuple[int, int]]:
        steps = []
        step_x, step_y = self._get_step(self.start)  # type: ignore
        while True:
            next_pos = self.start.__add__(step_x, step_y)  # type: ignore
            if next_pos == self.end:
                break
            elif not isinstance(next_pos, (int, float)):
                raise AssertionError("Non-numeric coordinate found in line segment.")
            steps.append((next_pos, None))
            self.start = next_pos
            step_x,