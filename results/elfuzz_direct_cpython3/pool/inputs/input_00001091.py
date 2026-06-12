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
U = TypeVar("U")

# ---------------------------------------------------------


class PriorityQueue(Generic[K, V]):
    """Priority Queue implementation.

    >>> pq = PriorityQueue()
    >>> pq.push(1, 'a')
    >>> pq.push(3, 'b')
    >>> pq.push(5, 'c')
    >>> pq.pop()
    ('b', 3)
    """

    def __init__(self) -> None:
        self._queue: list[tuple[int, K]] = []
        self._index: dict[K, int] = {}

    def push(self, key: K, val: V) -> None:
        if key in self._index:
            raise ValueError(f"Duplicate key: {key}")
        entry = (val, self._max_priority(), key)
        self._index[key] = len(self._queue)
        self._queue.append(entry)
        self.heapify()

    @overload
    def pop(self) -> tuple[Literal["", "value"], K]:
        ...

    @overload
    def pop(self) -> tuple[Literal["priority"], K]:
        ...

    def pop(self) -> tuple[str, K]:
        _, priority, key = self._queue.pop(0)
        del self._index[key]
        return ("value", key), priority

    def heapify(self) -> None:
        heapq.heapify(self._queue)

    @property
    def max_priority(self) -> K:
        try:
            _, priority = self._queue[-1]
            return priority
        except IndexError:
            raise ValueError("Empty queue") from None

    def peek(self) -> tuple[V, K]:
        _, value, key = self._queue[-1]
        return value, key

    def is_empty(self) -> bool:
        return not self._queue

    def update_priority(
        self, old_key: K, new_val: V, *, priority_type: str = ""
    ) -> None:
        index = self._index.get(old_key)
        if index is None:
            raise KeyError(f"{old_key} not found")
        entry = self._queue[index]
        _old_priority, _old_value, _old_key = entry
        _new_priority = (
            min(self.max_priority, _old_priority),
            max(-_old_priority, _old_priority),
        )
        new_entry = (_new_priority, new_val, old_key)
        self._queue[index]