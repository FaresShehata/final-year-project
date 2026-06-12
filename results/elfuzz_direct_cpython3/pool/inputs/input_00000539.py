"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def print_(*args: A | B | C) -> None:
    """
    >>> print_("foo", "bar", sep=" ")
    foo bar
    """
    print(" ".join(map(str, args)))


def plus(n1: int, n2: int) -> int:
    return n1 + n2


print_(plus(1, 2))  # 3


# Closure example
def make_incrementor(n: int) -> Callable[[int], int]:
    def inc(x: int) -> int:
        return x + n

    return inc


inc_by_one = make_incrementor(1)
inc_by_ten = make_incrementor(10)

assert inc_by_one(4) == 5
assert inc_by_ten(4) == 14


# Higher-order function example
def sum_of_squares(numbers: list[int]) -> int:
    return sum(map(lambda n: n * n, numbers))


assert sum_of_squares([1, 2, 3]) == 14


# Comprehension example
comp = [n for n in range(1, 6)]
assert comp == [1, 2, 3, 4, 5]


# Generator example
gen: Generator[str] = ("Hello" if i % 2 else "World" for i in range(3))
for item in gen:
    print(item)


# Coroutine example
async def count_up_to(limit: int) -> Iterator[int]:
    try:
        while True:
            value = yield from input_async()  # noqa: WPS421
            assert isinstance(value, str)
            if value.isdigit():
                number = int(value)
                if limit <= number:
                    raise StopIteration
                print(number)
            elif value.lower().startswith("q"):
                raise StopAsyncIteration
    except StopIteration:
        pass


async def main() -> None:
    async with count_up_to(10) as stream:
        await stream.send(None)
        await stream.send("1")
        await stream.send("2")
        await stream.send("3")
        await stream.send("7")
        await stream.send("9")
        await stream.send("q")

    print("done.")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        loop.close()


