"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import sys
import timeit


def non_generator():
    for i in range(10):
        print(i)


@contextlib.contextmanager
def non_coroutine():
    yield


async def coroutine():
    for i in range(10):
        await asyncio.sleep(.25)

# A number of data structures are available to you when working with iterable objects. These include:

# * lists
# * iterables
# * sequences and string literals
# * other collections such as dictionaries
# * tuples
# * set types


class GeneratorExample:
    """
    Generator Example
    """

    @staticmethod
    def my_generator() -> Iterable[Union[int, str]]:
        yield 'hello'
        yield 'world'

    @staticmethod
    async def my_async_generator() -> AsyncIterable[str]:
        yield 'hello'
        yield 'world'

    def simple_example(self):
        print("Generator example")
        print('for loop:')
        for value in self.my_generator():
            print(value)
        print('list comprehension:', list(self.my_generator()))
        print('set:', {value for value in self.my_generator()})
        print('dictionary:', dict(enumerate(self.my_generator())))

    async def simple_coroutine_example(self):
        print('Coroutine example')
        async for value in self.my_async_generator():
            print(value)

    def custom_iterator(self):
        print('Custom iterator')

        class MyIterator:
            def __init__(self):
                self.count = -1

            def __iter__(self):
                return self

            def __next__(self):
                if self.count == 9:
                    raise StopIteration()

                self.count += 1
                return f'Hello world {self.count}'

        print([value for value in MyIterator()])
        print(list(MyIterator()))

        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))

        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))

        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print(next(iter(MyIterator())))
        print        self._generator = generator_function()
        self._next_yielded_value = next(self._generator)
        self._stack = [self]

    def _step(self) -> bool:
        try:
            while True:
                yield self._next_yielded_value
                self._next_yielded_value = next(self._generator)
        except StopIteration as e:
