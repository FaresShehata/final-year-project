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

    print("--> await the result of the task's completion")
    print(f"result={await task}")

    print("--> create another coroutine from an async function")
    task2 = asyncio.create_task(main_2())
    print(
        f"coroutine created with id {id(task2)} and name '{task2.name}':"
    )

    print("--> wait for all tasks to complete")
    await asyncio.gather(task, task2)
    print("--> all tasks completed")


def search(iterable: Iterable[int], value: int, *, start=None) -> bool:
    """Binary search."""
    if len(iterable) == 0:
        return False
    midpt = len(iterable) // 2
