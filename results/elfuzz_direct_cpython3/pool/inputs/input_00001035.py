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
[(x, y) for x in range(3) for y in range(2)]
[(x, y) for x in range(3)]  # <- only one `y` iteration possible


# Generator expression example
generator_expression = (x ** 2 for x in range(3))
next(generator_expression)  # 0
next(generator_expression)  # 1
next(generator_expression)  # 4
next(generator_expression)  # StopIteration exception


def count_to(limit: int) -> Iterator[int]:
    current_number = 0
    while current_number < limit:
        yield current_number
        current_number += 1


count_generator = count_to(5)
for number in count_generator:
    print(number, end=" ")  # 0 1 2 3 4
    assert next(count_generator) == 5


# Generator example
def fibs() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


fibs_generator = fibs()

assert next(fibs_generator) == 0
assert next(fibs_generator) == 1
assert next(fibs_generator) == 1
assert next(fibs_generator) == 2
assert next(fibs_generator) == 3
assert next(fibs_generator) == 5


# Coroutine example
async def main():
    async with (
        StreamReader() as reader,
        StreamWriter() as writer,
    ):
        task = asyncio.create_task(reader.read_until(b"q"))
        writer.write("hello".encode())

        _, data = await asyncio.gather(task, writer.drain())

        print(data.decode())


async def test_main():
    async with (
        StreamReader() as reader,
        StreamWriter() as writer,
    ):
        await reader.readuntil(b"q")
        writer.write("9\n")
        await writer.drain()

        line = await reader.readline()
        assert line == b"6\n"

        writer.write("9\n")
        await writer.drain()

        line = await reader.readline()
        assert line == b"81\n"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    args = parser.parse_args(sys.argv[1:])
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(test_main())
    loop.close()


# Itertools examples
[_        await stream.send("9")
        await stream.send("q")

    print("done.")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        loop.close()


