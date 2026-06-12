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

    # Declare both attribute types at once using Alias
    class Student(Person):  # Inheritance example
        grade: float
        school: str

    # Declare the type of an instance variable by reference
    student_grade: float | None = None
    student_school: str | None = None

    # Declare the type of a function argument
    def greet(person: Person) -> list[str]:
        ...

    # Declare the type of a function return value
    def find_person(name: NameStr) -> tuple[NameStr, AgeInt, AddressStr]:
        ...

    # Declare a generic type parameter
    T = TypeVar("T", bound=Person)

    # Declare the type of a subclass argument
    def fetch_data(subject: T, *, start: int = 0, end: int | None = None) -> list[T]:
        ...

    # Declare the type of a callable argument
    def run_command(command: Callable[..., None]) -> None:
        command()


# Part 5: string parsing (tokenize, ast.literal_eval, textwrap, Formatter)
def part_5():
    # Parse Python source code into abstract syntax tree
    src_code = "print('Hello World')\n"
    tree = ast.parse(src_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            print(ast.dump(node.value))

    # Evaluate a literal expression
    expr_str = "4 + 7.9 / 2j"
    obj = ast.literal_eval(expr_str)
    print(obj)

    # Wrap long strings
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Suspendisse non lacus sed dui condimentum mattis. Morbi id
              nisl vitae diam pharetra pellentesque vel eu lectus."""
    wrapped_text = textwrap.fill(text, width=40)
    print(wrapped_text)

    # Format a string
    formatter = string.Formatter()
    record: dict[str, Any] = {"name": "Alice", "age": 25}
    formatted_string = formatter.v

# ── Annotated constraints (static-checked via TypeGuard) ─────────────────────

def is_int(x: Any) -> bool:
    try:
        return isinstance(int(x), int)
    except ValueError:
        return False


# ── dataclasses ──────────────────────────────────────────────────────────────

@dataclass(order=True)
class OrderedData:
    a: int
    b: float

    def __str__(self) -> str:
        return f"(a={self.a},b={self.b})"


@dataclass(eq=False)
class UnsortedData:
    a: int
    b: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnsortedData):
            return NotImplemented
        return self.a == other.a and self.b == other.b

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, UnsortedData):
            return NotImplemented
        return self.a < other.a or (self.a == other.a and self.b < other.b)



# ── abc.Numbers methods ──────────────────────────────────────────────────────

class NumberMixin(abc.Number):
    @property
    def microsecond(self) -> int:
        return self._microsec % 1_000_000

    def __round__(self, ndigits: int | None = None) -> T:
        rounded: T = round(float(self))
        return cls(rounded) if cls is not float else rounded


@dataclass(frozen=True)
class Timestamp(abc.Integral, abc.Repr, abc.Sized, abc.Hashable, NumberMixin):
    _seconds: int
    _microsec: int

    def __new__(
        cls: type[Timestamp],
        seconds: int | float = 0.0,
        *,
        microseconds: int = 0,
    ) -> Timestamp:
