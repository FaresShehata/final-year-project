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
    async def say_hello() -> str:
        return 'Hello'

    r = await say_hello()
    print(r)

    # Walrus Operator
    s = ('s' if (a := 'a') == 'a' else 'n')
    assert a == 'a'
    assert s == 's'

    # Structural Pattern Matching
    match {'A': 1, 'B': 2}:
        case {**d, 'C': 3}:  # unpack the dictionary d into other variables except C
            print(d['C'])

        case {key_1=value_1, key_2=value_2}:
            assert key_1 == value_1
            assert key_2 == value_2

    # typing.Generic
    class MyGeneric(typing.Generic[T]):
        ...

    my_generic_obj = MyGeneric[int](1)
    assert isinstance(my_generic_obj, MyGeneric[int])

    # typing.Literal
    assert typing.get_origin(type(Literal[True])) is Literal
    assert typing.get_args(type(True)) == (True,)
    assert typing.get_args(int.__instancecheck__) == (bool, int)

    # Exception Group
    try:
        raise ExceptionGroup(
            title='Exeptions',
            exceptions=[
                ValueError('ValueError 1'),
                KeyError('KeyError 2'),
            ]
        )
    except ExceptionGroup as e:
        for ex in e.exceptions:
            print(ex.args)
    else:
        print('No Exceptions!')

    # Exception Group
    exc_group = ExceptionGroup('Group', [
        TypeError('Type error'),
        AttributeError('Attribute error'),
        SyntaxError('Syntax error'),
    ])
    assert len(exc_group.exceptions) == 3
    assert isinstance(exc_group, ExceptionGroup)
    assert exc_group.title == 'Group'
    assert exc_group.with_traceback(None) is exc_group

    # Typing Protocol
    class Sequence(typing.Protocol):
        def __getitem__(self, index: typing.SupportsIndex) -> object:
            ...

        def __len__(self) -> int:
            ...

    assert isinstance(list(), Sequence)
    assert not isinstance(dict(), Sequence)

    # Slots
    class Person:
        __slots__ = ['name']

        def __init__(self, name: str) -> None:
            self.name = name

    p = Person(name='John Doe')

    # Dataclasses
    @dataclasses.dataclass(frozen=False)
    class Point# async for
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