"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import collections.abc as c_abc
import dataclasses as dcl
import functools
import inspect
import itertools
import math
import os
import queue
import re
import statistics
import sys
import threading
import timeit
import types
import typing
import weakref


def example_async():
    """asyncio: How to use async/await and get the return value"""

    def delay(seconds):
        print(f"Delaying {seconds} seconds...")
        time.sleep(seconds)

    async def delay_coroutine(seconds):
        print(f"Delaying {seconds} seconds...")
        await asyncio.sleep(seconds)

    loop = asyncio.get_event_loop()
    loop.create_task(delay(3))
    loop.run_until_complete(asyncio.gather(delay_coroutine(4), delay_coroutine(5)))
    loop.close()

    # Using 'await' inside a generator function is not recommended.
    # But you can write it like this:
    # https://stackoverflow.com/questions/619783/how-to-write-async-await-in-python-2
    # https://docs.python.org/3/library/inspect.html#types-and-type-hints
    # https://hamlestad.dev/posts/python-miscellaneous-coroutines/
    # https://docs.python.org/3/reference/datamodel.html#object.__aiter__

    async def gen(x):
        for i in range(x):
            yield i

    async def consumer():
        async for x in gen(5):
            print("Got", x)

    asyncio.run(consumer())

    # Using 'yield from'
    async def consumer_yield_from():
        async for x in gen(5):
            yield from [x]

    asyncio.run(consumer_yield_from())

    # Asynchronous context manager using 'with'
    class AsyncContextManager:
        async def __aenter__(self):
            print("Entering")

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("Exiting")

    async with AsyncContextManager() as cm:
        pass

    # Coroutine object
    coro = delay_coroutine(1)
    # Coroutine object does not have a __dict__. So we cannot call methods on it.
    # However, we can call functions that are annotated with @coroutine
    # (https://github.com/python/cpython/blob/main/Lib/async/__init__.py).
    # If you want to convert a coroutine object into a normal function, then use
    # the 'async_to_sync' decorator or convert it manually with
    # 'functools.partial': https://stackoverflow.com/a/67491760/15748831
    # https://www.pydanny.com/goodie-corn-slices.html
    # https://docs.python.org/3/library/functools.html#functools.partial
    # https://stackoverflow.com/questions/35293829/is-it-possible-with-functools-partial-to-pass-a-name-as-the-first-parameter-inst
    assert callable(coro)
    # The following line will raise an error because the coroutine has no '__name__' attribute.
    # assert coro.__name__ == "delay_coroutine"

    # Converting a coroutine object to a normal function with 'inspect.iscoroutinefunction'.
    coro_func = inspect.iscoroutinefunction(delay_coroutine)
    assert coro_func
    # We can execute the normal function just like a regular function.
    ret = coro_func(1)
    assert isinstance(ret, asyncio.Future)
    future = asyncio.ensure_future(ret)
    result = asyncio.run(future)
    assert result == None

    # Converting a coroutine object to a normal function with 'isinstance'.
    coro_obj = isinstance(delay_coroutine, asyncio.coroutines.Coroutine)
    assert coro_obj
    # We can execute the normal function just like a regular function.
    ret = coro_obj(1)
    assert isinstance(ret, asyncio.Future)
    future = asyncio.ensure_future(ret)
    result = asyncio.run(future)
    assert result == None

    # Converting a coroutine object to a normal function with 'inspect.isgeneratorfunction'.
    coro_gen = inspect.isgeneratorfunction(gen)
    assert coro_gen
    # We can execute the normal function just like a regular function.
    ret = coro_gen(1)
    assert isinstance(ret, asyncio.Future)
    future = asyncio.ensure_future(ret)
    result = asyncio.run(future)
    assert result == None

    # Converting a coroutine object to a normal function with 'inspect.signature'.
    sig = inspect