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
                # Just return a slice of the underlying iterable.
                return list(self)[start:stop]

            # Otherwise, we need to copy all the values manually.
            result: list[T] = []
            cache_idx = 0
            while True:
                try:
                    result.append(next(self))
                    cache_idx += 1
                except StopIteration:
                    break

            return result[start:stop]
        else:
            return next(iter(self.__iter__), None)


@dataclasses.dataclass(frozen=True)
class Point:
    """
    An immutable point class with integer x and y coordinates.

    >>> p = Point(x=1, y=2)
    >>> p.x
    1
    >>> p.y
    2
    >>> p.z
    Traceback (most recent call last):
      ...
    AttributeError: 'Point' object has no attribute 'z'
    """

    x: int
    y: int

    @classmethod
    def from_json(cls, s: str) -> Point:
        return cls(**json.loads(s))

    def __post_init__(self) -> None:
        assert isinstance(self.x, int)
        assert isinstance