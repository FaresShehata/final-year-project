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

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Rational):
            return NotImplemented
        return self.to_float() == o.to_float()

    def __lt__(self, other: Rational) -> bool:
        return self.to_float() < other.to_float()

    def __hash__(self) -> int:
        return hash((self.numerator, self.denominator))


r1 = Rational.from_float(1.0 / 3)
r2 = Rational.from_float(0.3333333333333333333333333333333333333333333333)
print(r1, r2)
assert r1 == r2
assert r1 < r2
assert hash(r1) != hash(r2)


# #4
def add(x: int | None, y: int | None) -> int | None:
    if x is None or y is None:
        return None
    return x + y


# #5
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


primes = [i for i in range(100_000) if is_prime(i)]


def prime_counting_function(n: int) -> int:
    return len([x for x in primes if x < n])


# #6
def prepare_html(html: str, **kwargs: str) -> str:
    tag_name = kwargs.pop("_tag")
    attrs = "".join(f' {k}="{v}"' for k, v in kwargs.items())
    return f"<{tag_name}{attrs}>{html}</{tag_name}>"


print(prepare_html("<h1>hello world</h1>", _tag="div"))


# #7
async def sleep_and_print(name: str, delay: float) -> None:
    await asyncio.sleep(delay)
    print(name)


async def main2():
    await asyncio.gather(sleep_and_print("foo", 0.5), sleep_and_print("bar", 0.3))

   