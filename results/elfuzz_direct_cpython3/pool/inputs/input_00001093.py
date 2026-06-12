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


def Dataclasses() -> DataClassA:
    return DataClassA(x=1, y=2)


def enumerate_with_dataclasses() -> DataClassA:
    da = DataClassA(x=1, y=2)
    for i, d in enumerate(da):
        print(i, d)
    return da


def EnumToDict() -> dict[AsyncEnum, int]:
    e = DataClassA._member_map_
    return {k: v.value for k, v in e.items()}


def Exceptions() -> ExceptionGroup:
    try:
        raise ValueError("foo")
    except ValueError as e:
        raise RuntimeError("bar") from e


def Generics() -> list[Tuple[Sequence[int], Sequence[float]]]:
    seq1 = [1, 2]
    seq2 = [1.0, 2.0]
    return [(seq1, seq2)]


def WalrusOperator() -> None:
    while (i := len(list(range(10)))) < 20:
        print(i)


def WalrusOperatorWithUnpack() -> None:
    l = [*range(20)]
    while (i := len(l)) < 20:
        print(i)


async def main():
    await asyncio.gather(*[a_test_case(x) for x in range(10)])

asyncio.run(main())


def a_async_generator() -> Iterator[Tuple[int, float]]:
    yield (1, 1.0)
    yield (2, 2.0)


def a_async_iterator() -> Iterator[int]:
    yield from (x * x for x in range(10))


async def a_async_iterable() -> Iterable[int]:
    return (x * x for x in range(10))


async def b_async_generator() -> Iterator[Tuple[int, float]]:
    def gen():
        for item in ((1, 1.0), (2, 2.0)):
            yield item
    yield from gen()


def b_async_iterator() -> Iterator[int]:
    it = iter((x * x for x in range(2)))
    while True:
        try:
            yield next(it)
        except StopIteration:
            break


async def b_async_iterable() -> Iterable[int]:
    return iter((x * x for x in range(2)))


async def c_yield_from() -> Generator[int, None, None]:
    async for i in a_async