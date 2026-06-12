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


def generate_func(
    *args: A | B | Callable[A, B] | None, **kwargs: str | int | Callable[Any, Any]
) -> list[tuple[str, Any]]:
    """Generate a list of tuples with the given arguments and keyword arguments.

    Args:
        *args:
            Variable length argument list.
        **kwargs:
            Arbitrary keyword arguments.

    Returns:
        List of tuples containing the provided arguments and keyword arguments.
    """
    return [tuple(args)] + [(key, val) for key, val in kwargs.items()]


# Closure example, which is a nested function that captures the local variables from its enclosing scope.


def outer_function(x):
    def inner_function(y):
        return x + y

    return inner_function


# Higher-order function example: map(), filter()
numbers = [1, 2, 3, 4, 5]
squared_numbers = list(map(lambda x: x**2, numbers))  # Using map to square each number
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))  # Using filter to get even numbers
print(squared_numbers)
print(even_numbers)

# Comprehension examples
cubes = [x**3 for x in range(1, 6)]
factors_of_9 = [i for i in range(1, 10) if 9 % i == 0]

# Generators example:
generator_obj = (x**2 for x in range(5))
next(generator_obj)  # Output: 0
next(generator_obj)  # Output: 1
for num in generator_obj:
    print(num)  # Output: 4, 9, 16, 25

# Coroutines example:
async_generator = (num async for num in range(5))


class AsyncGenerator:
    def __init__(self, func: Callable[[], Coroutine]) -> None:
        self.func = func

    async def __aiter__(self) -> AsyncGenerator:
        return self

    async def __anext__(self) -> int:
        result = await call(self.func())
        return result


coroutine_result = AsyncGenerator(lambda: asyncio.coroutine(lambda: 42))[0]()
print(coroutine_result)  # Output: 42

# Itertools example: itertools.count(), itertools.chain(),
#                    itertools