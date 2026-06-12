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
    TypeAlias,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing_extensions import Self


class CyclicList(Generic[T]):
    """
    A cyclic list.

    >>> c = CyclicList(range(4))
    >>> for i in range(len(c) * 3):
    ...     print(c[i])
    0
    1
    2
    3
    0
    1
    2
    3
    0
    1
    2
    3
    """

    _cache: tuple[Iterator[T], int]

    def __init__(self, items: Iterable[T]) -> None:
        self._cache = iter(items), len(items) - 1

    def __len__(self) -> int:
        return len(self._cache[0])

    def __getitem__(self, item: int | slice) -> T | list[T]:
        if isinstance(item, slice):
            start, stop, step = item.start or 0, item.stop or len(self), item.step or 1
            if not (start < stop and step > 0):
                raise ValueError("slice indices must be integers")

            if step == 1:
                return self[start : stop + 1]
            else:
                result: list[T] = []
                while True:
                    chunk_length = min(stop - len(result), len(self) - start)
                    result.extend(next(self._cache)[start:start + chunk_length])
                    start += chunk_length
                    if start >= stop:
                        break
                return result
        elif isinstance(item, int):
            if item < 0:
                item %= len(self)
            return next(self._cache)[item]


def fib(n: int) -> int:
    """Fibonacci sequence."""
    a = b = 1
    for _ in range(n):
        yield a
        a, b = b, a + b


async def fibonacci_async() -> Iterable[int]:
    """Async Fibonacci sequence."""
    a = b = 1
    while True:
        yield a
        a, b = b, a + b


@dataclasses.dataclass(order=True, frozen=False)
class Point:
    x: float
    y: float

    @classmethod
    def from_str(cls, s: str) -> Point:
        """Create a point from a string."""
        match = re.match(r"^(?P<x>-?\d+\.\d+)\s+(?P<y>-?\d+\.\d+)$", s)
        assert match is not None
        return cls(**match.groupdict())


class Direction(enum.Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

    def reverse(self) -> Direction:
        """Return the opposite direction."""
        mapping = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return mapping[self]


@enum.unique
class Gender(enum.IntEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3


@enum.unique
class GenderType(enum.Enum):
    M = "Male"
    F = "Female"


# https://mypy.readthedocs.io/en/stable/kinds_of_types.html#protocols-and-structural-typing
class AsyncIterable(Protocol):

    def __aiter__(self) -> AsyncIterator[Any]: ...


@enum.unique
class CountryCode(enum.IntEnum):
    SG = 9876543210
    US = 12345			self._lines.append(line)
			col_no += len(lines[pos])
			if b'\r' in lines[pos]:
				line_no += 1
				col_no -= lines[pos].index(b'\r')
			elif b'\n' in lines[pos]:
				line_no += 1
				col_no = 0
			pos += 1


	@property
