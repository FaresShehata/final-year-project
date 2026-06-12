"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import collections.abc
import contextlib
import functools
import itertools
import types
import typing
import unittest.mock as mock


class Task:
    """Asyncio task decorator."""

    def __init__(self, function: typing.Callable) -> None:
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


async def main():
    # async decorator
    @Task
    async def echo(text: str) -> str:
        print("Received", text)
        await asyncio.sleep(1)
        return text.upper()

    # async with
    async with open('test.txt') as file:
        print(file.read())


def _is_even(n: int) -> bool:
    return n % 2 == 0


# async for
async def square_generator() -> typing.AsyncGenerator[int]:
    i = 0
    while True:
        yield (i := i + 1)**2


@contextlib.contextmanager
async def coroutine_manager(coroutine_func):
    try:
        await coroutine_func()
        yield
    finally:
        pass


# async def test_context():
#     with coroutine_manager(asyncio.create_task(square_generator())) as x:
#         await asyncio.gather(*(x for _ in range(3)))


# generic type hinting
T_co = typing.TypeVar('T_co', covariant=True, bound=int)
U = typing.TypeVar('U')
V = typing.TypeVar('V')


def func(a: T_co, b: U = 12345, c: V | None = None) -> None:
    """
    Args:
        a (:obj:`int`): integer value.
        b (:obj:`str`, optional): string value, default is ``'hello world!'``
        c (:obj:`None` or :obj:`int`, optional): an `int` value or `None`
    Returns:
        None
    """

    print(f'a={a}, b={b}, c={c}')


def get_list_bounded_by_range(l, start=1, end=None) -> list[int]:
    return [item for item in l if start <= item < end]


# Context Manager and AsyncContextManager
class AsyncContextManagerBase(asyncio.AbstractAsyncContextManager):
    def __init__(self, _state: None):
        super().__init__()
        self._state = _state