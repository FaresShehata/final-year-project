"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses as dc
import enum
import functools
import itertools
import logging
import math
import random
import re
import statistics
import sys
import types
import typing as ty
from collections.abc import (
    AsyncIterator,
    Iterator,
    Sequence,
)
from datetime import (
    date,
    datetime,
    time,
)
from pathlib import Path
from pprint import pformat
from string import Template
from types import ModuleType
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
)

import pendulum


# Task 1: async/await basics
async def main() -> None:
    print("main coroutine started")
    # create a coroutine from an async function
    task = asyncio.create_task(
        foo_async(), name="task-foo", trace=True, priority=5
    )
    # await the result of the task's completion
    print(f"result={await task}")
    print("main coroutine finished")


async def foo_async() -> int:
    print("--> foo_async")
    return 42


@dc.dataclass
class Foo:
    bar: str
    baz: int

    @classmethod
    @functools.cache
    async def new(cls) -> Foo:
        print("--> classmethod new()")
        return cls(bar="", baz=0)


async def main_2() -> None:
    print("\nTask 1: async/await basics")

    print("--> create a coroutine from an async function")
    task = asyncio.create_task(foo_async())
    print(f"coroutine created with id {id(task)} and name '{task.name}'")

    print("--> wait for the task to complete (with timeout)")
    try:
        (result,) = await asyncio.wait_for(task, timeout=3.0)
    except asyncio.TimeoutError:
        print("Timeout error (see log)")
        return
    print(f"result={result}")


def main_3() -> None:
    print("\nTask 1: async/await basics\n")

    print("--> Main thread performs cleanup on exit.")
    shutdown = object()

    print("--> Create event loop.")
    loop = asyncio.get_event_loop()
    assert isinstance(loop, asyncio.AbstractEventLoop), type(loop)
    print(f"loop is {type(loop).__name__}")

    print("--> Run tasks that use the event loop.")
    loop.run_until_complete(main())

    print("--> Shutdown event loop.")
    loop.close()


def _run_tasks(tasks: list[asyncio.Task], max_workers: int | None) -> None:
    if not (max_workers or max_workers == 0):
        tasks = [t for t in tasks if t.cancel()]
        loop = asyncio.get_running_loop()
        for task in tasks:
            task.add_done_callback(lambda f: loop.call_exception_handler({"message": "test"}))
        tasks.clear()
        loop.call_soon_threadsafe(asyncio.gather(*tasks))

    elif max_workers < 1:
        raise ValueError("max_workers must be positive.")

    else:
        futures = []
        while True:
            done, pending = yield from asyncio.wait(tasks[:max_workers])
            for future in done:
                tasks.remove(future)
            futures.extend(pending)
            if not tasks:
                break


async def run_tasks_max_workers(max_workers: int) -> None:
    tasks = [
        asyncio.create_task(_worker(i)) for i in range(6 * 8 - 1)
    ]
    loop = asyncio.get_running_loop()
    loop.create_task(_run_tasks(tasks=tasks, max_workers=max_workers))


async def _worker(n: int) -> None:
    print(f"{n} start")
    await asyncio.sleep(0.01)
    print(f"{n} end")


async def demo_run_tasks_max_workers() -> None:
    print("Demo 'run_tasks' with various values of 'max_workers'.")
    for max_workers in (None, 0, -1, 1, 2, 5, 7, 9, 10, 11, 15,     midpt = len(iterable) // 2
