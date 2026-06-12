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
    f = lambda x: g(x, 1)
    assert f(7) == 8
    d = {"a": [1], "b": ["foo", "bar"]}
    dd = {k: v for k, v in [(x, f(int(y))) if isinstance(y, str) else (y, f(k)) for x, y in d.items()]}

    print(dd)

    def func_with_closing():
        x = 6
        a = "panda"

        def inner_func():
            nonlocal x
            nonlocal a
            x += 1
            a += "!"

        inner_func()
        return x, a

    print(func_with_closing())  # (7, 'panda!')

    # Higher-order functions
    print(functools.reduce(operator.mul, range(6)))
    print(list(map(operator.add, range(3), range(3))))
    print(
        list(filter(lambda x: x % 2 != 0 and x >= 0, range(-3, 4))),  # [-3, -1]
    )
    print([i**2 for i in range(10)])
    print(list(itertools.takewhile(lambda x: x < 10, [1, 2, 3, 4])))


if __name__ == "__main__":
    main()