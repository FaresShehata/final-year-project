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
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
)

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import Self


# #1
class AsyncGenerator(NamedTuple):
    """An asynchronus generator of arbitrary items."""

    async def __aiter__(self) -> Self:
        raise NotImplementedError()

    async def __anext__(self) -> Any:
        raise NotImplementedError()


async def stream() -> AsyncGenerator[int]:
    yield 1
    for i in range(5):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        yield i + 2


async def main():
    async with (AsyncGenerator(await stream()) as g):
        print(type(g), end=" ")
        while True:
            try:
                item = await g.__anext__()
            except StopAsyncIteration:
                break
            else:
                print(item, end=" ")
    # <typing.List[<type 'int'>]> 1 2 3 4 5
    print()


asyncio.run(main())


# #2
@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int


def compare_people(a: Person, b: Person) -> bool:
    return a.name == b.name and a.age == b.age


print(
    sorted(
        [
            Person("John", 29),
            Person("Alice", 28),
            Person("Bob", 30),
            Person("John", 29),
        ],
        key=compare_people,
    )
)


# #3
@dataclasses.dataclass(frozen=False)
class Rational:
    numerator: int
    denominator: int

    @classmethod
    def from_float(cls, value: float) -> Self:
        return cls(int(value * 10**6), 10**6)

    def to_float(self) -> float:
        return self.numerator / self.denominator

    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self) -> str:
        return f"Rational({self.numerator}, {self.denominator})"


print(Rational.from_float(2))
print(str(Rational.from_float(2)))
print(repr(Rational.from_float(2)))


