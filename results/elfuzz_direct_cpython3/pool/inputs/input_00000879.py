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
D = TypeVar("D")


def double(x: int) -> int:
    return x * 2


def main() -> None:

    # Closures
    print(double(5))  # 10
    print((lambda x: x + 1)(double(5)))  # 11
    print(lambda x: x ** 2)((lambda y: y * 4)(5))  # 81
    g = lambda x, y: x + y
    print(g(7, 9))  #
    f = lambda x, y: x(y)
    def square(z):
        return z**2
    print(f(square, 5))

    # Higher-order functions
    print(max([1, 6, -3, 3]))
    print(max(1, 6, -3, 3))
    print(max([1, 6], default=99))
    print(min([1, 6, -3, 3]))
    print(sum([1, 6, -3, 3]))

    # Comprehensions & Generators
    print({x for x in range(10)})
    print([x for x in range(10)])
    print(tuple(x for x in range(10)))
    print(list(map(str, [1, 2, 3])))
    print(*[x for x in range(10)])

    # Coroutines
    class EchoOnEnterExit:
        def __init__(self, value: str | bytes) -> None:
            self.value = value

        async def __aenter__(self) -> Self:
            print(f"Writing {self.value} to stdout...")
            sys.stdout.write(self.value.decode())
            await asyncio.sleep(1)
            return self

        async def __aexit__(self, exc_type: type, exc_value: Exception, tb: TracebackType) -> bool:
            print()
            print(f"Done writing {self.value}. Exiting coroutine.")
            return True

    loop = asyncio.get_event_loop()
    try:
        async with EchoOnEnterExit(b"Hello world\n"):
            pass
    finally:
        loop.close()

    # Itertools
    print(list(itertools.takewhile(lambda x: x < 10, [1, 2, 3, 4])))


if __name__ == "__main__":
    main()