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
from uuid import UUID as _UUID

if TYPE_CHECKING:
    from collections.abc import Coroutine, Iterable, MutableMapping, Sequence


class UUID(_UUID):
    """Alias for uuid.UUID"""


C = TypeVar("C")
V = TypeVar("V")


# TODO: use with `type` instead of `typing_extensions`
@runtime_checkable
class SupportsLessThan(Protocol[C]):
    def __lt__(self, other: C) -> bool: ...


T = TypeVar("T", bound=SupportsLessThan)


def fast_sort(iterable: Iterable[T], *, key=lambda t: t) -> list[T]:
    """
    >>> fast_sort(["b", "a"]) == sorted(["b", "a"])
    True
    >>> fast_sort([1, -3]) == sorted([1, -3])
    True
    """
    return [x for x in iterable if key(x) is not None]


def fast_sort_in_place(iterable: MutableSequence[T], *, key=lambda t: t) -> None:
    """In-place version of :func:`fast_sort`."""
    for i in range(len(iterable)):
        min_i, min_v = i, key(iterable[i])
        for j in range(i + 1, len(iterable)):
            v = key(iterable[j])
            if min_v is None or v < min_v:
                min_i, min_v = j, v

        # swap
        iterable[min_i], iterable[i] = iterable[i], iterable[min_i]

        # update min_v to avoid unnecessary comparisons
        min_v = key(min_v)


async def sleep(seconds: float | int) -> None:
    await asyncio.sleep(float(seconds))


def measure(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    @dataclasses.dataclass(frozen=True)
    class TimeResult:
        start_time: float
        end_time: float
        duration_ms: float
        result: T

    async def wrapper(*args: Any, **kwargs: Any) -> TimeResult:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        return TimeResult(start_time=start_time, end_time=end_time, duration_ms=(end_time - start_time) * 1000, result=result)

    return wrapper


class Storage(Generic[T]):
    def __init__(self) -> None:
        self._store: dict[int, T] = {}

    def add(self, item: T, *, index: int = 0) -> int:
        assert 0 <= index < (max(self._store.keys()) + 1), f"Index out of bounds {index}"
        self._store[index] = item
        return index

    def get(self, index: int) -> T:
        return self._store.get(index, None)

    def pop(self, index: int) -> T | None:
        removed_item = self._store.pop(index, None)
        assert removed_item is not None, f"{index} not found"
        return removed_item

    def __len__(self) -> int:
        return len(self._store)

    def keys(self) -> set[int]:
        return set(range(max(self._store.keys(), default=0)))

    def values(self) -> set[T]:
        return set(self._store.values())

    def items(self) -> set[tuple[int, T]]:
        return set(self._store.items())


class PriorityQueue(Generic[T]):
    def __init__(self) -> None:
        self._queue: list[tuple[float, T]] = []  # [(priority, value)]

    def contains(self, value: T) -> bool:
        return any(value == v for _, v in self._queue)

    def insert(self, priority: float, value: T) -> None:
        heapq.heappush(self._queue, (priority, value))

    def remove(self, value: T) -> None:
        for i, (prio, val) in enumerate(self._queue):
            if val == value:
                del self._queue[i