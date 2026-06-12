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
    Sequence,
    Tuple,
    TypeAlias,
    Union,
)

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import ParamSpec
else:
    class P: pass
    P = P()

# TODO: Add a link to the official docs about "async all" and "async any"

class AsyncEnum(enum.Enum):
    """An abstract base class for asynchronous enumerations."""

    @classmethod
    def _generate_next_value_(
        cls: type[AsyncEnum],
        value: str | int,
        start: int | None = None,
        count: int | None = None,
        last_values: list[str] | None = None,
    ) -> str:
        return value


@dataclasses.dataclass(frozen=True)
class DataClassA:
    x: int
    y: int


@dataclasses.dataclass(frozen=True)
class DataClassB(DataClassA):
    z: int


def Counters() -> dict[int, Counter]:
    c1 = Counter([1, 2, 3])
    c2 = Counter([4, 5])
    return {c1[1]: c2}


def DataClasses() -> tuple[tuple[DataClassA, ...], tuple[DataClassB, ...]]:
    da1 = DataClassA(1, 2)
    da2 = DataClassA(3, 4)
    db1 = DataClassB(1, 2, 3)
    db2 = DataClassB(4, 5, 6)
    return (da1, da2), (db1, db2)


def DefaultDicts() -> defaultdict[int, int]:
    d = defaultdict(int)
    d.update({i: i ** 2 for i in range(5)})
    return d


def Deques() -> deque[float]:
    dq = deque()
    dq.append(float('nan'))
    return dq


def Enumerators() -> tuple[Tuple[int, int], tuple[int, float]]:
    a = enumerate((1, 2))
    b = enumerate(('a', 'b'), 1.5)
    return next(a), next(b)


def Exceptions() -> tuple[Exception, ExceptionGroup]:
    try:
        raise ValueError('oh noes!')
    except BaseException as e:
        try:
            raise TypeError('oops again') from e
        except ExceptionGroup as e