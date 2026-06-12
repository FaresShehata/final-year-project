"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    Union,
)
from typing_extensions import get_args, get_origin


# Part 1: Thread and process pool executor
def part_1():
    # Create a thread pool with 3 worker threads
    # TODO: Create a thread pool with 2 worker threads
    pool = ThreadPoolExecutor(3)

    def func(i):
        return i * i

    for i in range(10):
        print("Thread:", pool.submit(func, i))
    print("\n")

    # Create a process pool with 4 processes
    # TODO: Create a process pool with 8 processes
    pool = ProcessPoolExecutor()
    for i in range(10):
        print("Process:", pool.submit(str.upper, f"Hello {i}"))
    print("\n")


# Part 2: Asyncio (async/await)
def part_2():
    async def sleep_async(delay: int | float):
        await asyncio.sleep(delay)

    async def main():
        t1 = time.time()
        await asyncio.gather(
            sleep_async(1), sleep_async(2), sleep_async(3), sleep_async(4)
        )
        t2 = time.time()
        print(f"Asynchronous execution took {t2 - t1:.2f}s")
        print()

        t1 = time.time()
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(sleep_async(i)) for i in range(1, 5)]
        loop.run_until_complete(asyncio.wait(tasks))
        t2 = time.time()
        print(f"Synchronous execution took {t2 - t1:.2f}s")

    import asyncio

    asyncio.run(main())


# Part 3: Context manager
async def part_3():
    from contextvars import copy_context

    async def outer():
        c = copy_context()
        yield c

    async def inner(c: copy_context()):
        original_value = c.token
        c_token = c.token
        assert original_value != c_token
        c.swap(original_value)

    async def main():
        with (await outer()) as c:
            async with inner(c=c) as c:
                pass

    asyncio.run(main())


# Part 4: type hints
def part_4():
    def my_func(a: int) -> str:
        return str(a)

    print(my_func.__annotations__)
    print(get_args(int))
    print(get_origin(int))

   