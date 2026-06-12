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


def func_closure() -> tuple[str, int]:
    """Closure example."""
    x: str = "hello world"
    y: int = 21

    def foo(a: int) -> int:
        return a + 42

    def bar(b: str) -> str:
        return b + x

    return foo(5), bar("!!!")


def func_higher_order() -> None:
    """High order function example."""


def func_comprehension() -> list[int]:
    """Comprehension example."""
    nums: list[int] = [x for x in range(-9, 10)]
    return [n for n in nums if n > 0 and n % 7 == 0]


def func_generator() -> Generator[int, None, None]:
    """Generator example - yield from."""
    for i in range(10):
        yield i * 2


def func_coroutine_send_throw_close() -> None:
    """Coroutine send example; also throw and close.

    Coroutines are objects that can receive data using the `send` method.
    They can be closed using the `close` method. The `next` built-in is not available to coroutine types.

    To start or resume resuming a coroutine, you need to use its .send() method with an initial value as parameter.
    This will make Python call the first line of code of your generator function, which by default is a statement called “yield”.

    The `send()` method returns either the next yielded value, raises StopIteration when it has finished yielding values,
    or raises Exception when your coroutine was created through the `throw()` method. It also receives an object as argument
    the exception to raise in case it needs to stop the iteration.

    With the `close()` method, we tell the coroutine that we’re done sending values into it.
    After calling this method, any subsequent calls to send() will result in StopIteration being raised.

    We say that a coroutine is cooperative because the caller must explicitly manage the state transitions between waiting and running.
    """

    def my_coro() -> Iterator[int]:

        while True:
            print(f"Before {yield}")
            try:
                val = yield
                # print(f"After {val}", end="")

            except ValueError:
                pass
            else:
                print(val)

    my