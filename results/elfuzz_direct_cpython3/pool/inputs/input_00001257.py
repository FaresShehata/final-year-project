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


# Part 4: type hints, type aliases
def part_4():
    class Person:  # A class with attributes and no method definitions
        name: str
        age: int
        address: str

    # Use a type alias to declare the type of an instance variable
    NameStr = str
    AgeInt = int
    AddressStr = str
    PersonType = tuple[NameStr, AgeInt, AddressStr]

    # Declare a function parameter's type using a type annotation
    def foo(person: PersonType) -> None:
        ...

    # Declare a function return value's type using a type hint
    def bar() -> PersonType:
        ...

    # Declare a variable's type using a type annotation
    person: PersonType = ("Alice", 30, "123 Main St.")

    # Declare a variable's type that is not explicitly annotated
    # by including it in a function signature or expression
    name = "Bob"
    address = "456 Elm St."

    # Declare multiple variables' types using a type alias
    p1, p2, p3: PersonType = ("Charlie", 25, "789 Maple Ave."), ("David", 28, "101 Pine Ln."),
    ("Eve", 32, "234 Oak Dr.")


# Part 5: functools
def part_5():
    # The @total_ordering decorator can be used to define only the three methods
    # in a class that implement the less than (<) relationship.
    # It automatically generates the rest of the comparison methods (__eq__ and __ne__)
    from dataclasses import dataclass
    from functools import total_ordering

    @dataclass(order=True)
    class Student:
        grade: int
        avg_score: float
        name: str = ""

    s1 = Student(grade=9, avg_score=9.5, name="Alice")
    s2 = Student(grade=9, avg_score=9.5, name="Bob")
    s3 = Student(grade=10, avg_score=9.5, name="Charlie")

    assert s1 < s2
    assert s1 <= s2
    assert not (s1 > s2)
    assert not (s1 >= s2)
    assert s1 == s2
    assert not (s1 != s2)

    assert s2 < s3
    assert s2 <= s3
    assert not (s2 > s3)
    assert not (s2 >= s3)
    assert not (s2 == s3)
    assert s2 != s3

    assert s1 < s3
    assert s1 <=

@functools.total_ordering
class ConcreteClassA(AbstractClassA):
    x: int


class AbstractClassB(metaclass=RegistryMeta):
    y: int


@functools.total_ordering
class ConcreteClassB(AbstractClassB):
    y: int

    @property
    def z(self):
        return self.y * 2


if __name__ == "__main__":
    assert len(RegistryMeta._registry["AbstractClassB"]) == 1
    print(*sorted(RegistryMeta._registry.values()), sep="\n")
    # ConcreteClassB