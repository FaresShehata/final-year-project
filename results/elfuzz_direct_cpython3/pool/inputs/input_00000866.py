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
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float

# ── class / decorator ────────────────────────────────────────────────────────

class MyFunction:
    def __call__(self, x: int) -> int:
        return x + 1


def add_one(x: int) -> int:
    return x + 1


# ── dataclasses ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int


def create_person(name: str, age: int) -> Person:
    return Person(name=name, age=age)


# ── functools ────────────────────────────────────────────────────────────────

def foo(*args: int, **kwargs: str) -> None:
    pass


def bar() -> None:
    foo(1, 2, 3, a=1, b=2, c=3)


# ── generator expressions ─────────────────────────────────────────────────────

# Yield from is the same as using yield inside of another generator.
async_generator = (
    value async for value in some_async_iterable if condition(value)
)


def generate_numbers(max_num: int) -> Generator[int, None, None]:
    """
    Generate a sequence of integers from 0 to `max_num - 1`.
    """

    for i in range(max_num):
        yield i


# ── inspect ──────────────────────────────────────────────────────────────────

def inspect_function(func: Callable[P, T]) -> None:
    """
    Print information about a function.

    Args:
        func: The function to inspect.
    """

    print(inspect.getfullargspec(func))


inspect_function(add_one)


# ── itertools ────────────────────────────────────────────────────────────────

numbers = [1, 2, 3]
squares = map(lambda n: n**2, numbers)
print(list(squares))  # Output: [1, 4, 9]

cubes = itertools.starmap(pow, [(x,) for x in range(10)])
print(list(cubes))  # Output: [0, 1, 8, 27, 64, 125, 216, 343, 512, 729]


# ── json, typing, typeshed ───────────────────────────────────────────────────

json_value: JsonValue        result = func([locks[i], dummy_list[i]] for i in range(len(dummy_list)))

    assert result == expected_result


def test_signal_handler():
    """Test signal handling."""

    def my_function(x: int, y: int):
        return x * y

    print(my_function(1, 2))
    print(my_function.__name__)
    print(type(my_function))

    try:
        raise ValueError("oops")
    except ValueError as e:
        print(e.args[0])


def test_thread_join_timeout():
    """Test join timeout"""
    first_thread = threading.Thread(
        target=lambda: time.sleep(1.0), name="first_thread"
    )
    second_thread = threading.Thread(
        target=lambda: time.sleep(2.0), name="second_thread"
    )
    first_thread.start()
    second_thread.start()
    try:
        first_thread.join(timeout=2.0)
        second_thread.join(timeout=2.0)
    finally:
        first_thread.join()
        second_thread.join()


def test_multiprocessing():
    """Test multiprocessing."""
    num_processes = 8
    results_queue = queue.Queue()

    class WorkerProcess(multiprocessing.Process):
        def run(self