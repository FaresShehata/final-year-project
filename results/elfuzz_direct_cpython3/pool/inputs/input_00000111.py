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


def make_random_string(n: int | None = None) -> str:
    """
    Generate a string of length n filled with random lowercase letters.
    """
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n or 5))


def first_non_none(*args: T | None | None) -> T | None:
    try:
        return next(filter(None, args))
    except StopIteration:
        return None


def last_non_none(*args: T | None | None) -> Optional[T]:
    try:
        return next(reversed(filter(None, args)))
    except StopIteration:
        return None


def weighted_choice(choices: dict[V, float]) -> V:
    total_weight = sum(c.weight for c in choices.values