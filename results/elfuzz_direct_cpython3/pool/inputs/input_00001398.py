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
    requests:   int


# ── ClassVars ────────────────────────────────────────────────────────────────

COUNTER: ClassVar[int]
CALLS:   ClassVar[int]


def _get_counter() -> int:
    return COUNTER


def _set_counter(counter: int) -> None:
    global COUNTER
    COUNTER = counter


def _increase_counter() -> None:
    global CALLS
    CALLS += 1


# ── Function parameters & return values ───────────────────────────────────────

def my_function(
    x: int,
    y: str,
    z: tuple[float, ...],
    a: dict[str, int],
    b: set[str],
    c: list[tuple[int, float]],
    d: list[str] | None
) -> dict[str, int]:
    pass


def my_generator_func(a: int, /, b: str, *, c: float) -> None:
    yield from range(3)


def my_coroutine(coro: Generator[Any, Any, Any]) -> None:
    next(coro)
    coro.send(None)


def coroutine_send(coroutine: Generator[Any, Any, Any], value: Any) -> None:
    try:
        coroutine.send(value)
    except StopIteration:
        pass


async def async_generator_func(x: int, y: str, *args: int, **kwargs: float) \
                        -> Iterable[float]:
    await asyncio.sleep(2.0)
    yield 1.0 + x + len(y) + sum(args) + sum(kwargs.values())


def async_coroutine(async_gen: AsyncGenerator[Any, Any]) -> None:
    loop = asyncio.get_event_loop()
    task = asyncio.create_task(async_gen.__anext__())
    loop.run_until_complete(task)
    loop.run_until_complete(async_gen.aclose())


async def asynchronous_for_loop(gen: AsyncIterator[T]) -> None:
    async for item in gen:
        print(item)


# ── Unpacking arguments and keyword arguments ────────────────────────────────

x = [1, 2, 3]
y = ["a", "b"]
z = {"c": 4}
x, *y, z = zip(x, y, z)


# ── Keyword-only arguments ──────────────────────────────────────────────────

def func(*, key="value") -> str:
    return key


func(key="hello")

"""TypeError: func() got some positional only arguments passed as keyword arguments
    func(key="hello")"""


func(key="world")


"""TypeError: func() got an unexpected keyword argument 'key'
    func(key="hello", key="world")"""


# ── Positional-only arguments ────────────────────────────────────────────────

def func(positional_only_arg, *, default_keyword_only_arg: int = 76) -> None:
    print(default_keyword_only_arg)


func(positional_only_arg=3.14, default_keyword_only_arg=69)


"""TypeError: func() got multiple values for argument 'positional_only_arg'"""


# ── `*` and `**` operators ──────────────────────────────────────────────────

x = [*range(3), *[i * 10 for i in range(3)]]
print(x)


y = {**{"one": 1}, **{"two": 2}}
print(y)


# ── Variable-length arguments ────────────────────────────────────────────────

def f(*var_args: object, **kwarg_dict: object) -> None:
    pass


f()


f(1, 2, 3, a=1, b=2, c=None)


# ── Default arguments ────────────────────────────────────────────────────────

def foo(bar: int = 1, baz: str = "default") -> None:
    ...


foo()

foo(baz="abc")

foo(13)

try:
    foo(baz=[1])
except TypeError:
    ...


# ── Anonymous functions ──────────────────────────────────────────────────────

add_one = lambda x: x + 1

assert add_one(2) == 3

# │ The following is equivalent to the above line.
# │ It's useful when you need to use a lambda function once or two times.

lambda x: x + 1

# │ The following is equivalent to the above lines.
# │ It's useful when you need to use a lambda function many times.

[(lambda x: x + 1)(i) for i in range(3)]

# │ The following is equivalent to the above line.
# │ It's useful when you don't want to assign a variable to the lambda function.

[i + 1 for i in range(3)]

# ── Lambda functions with keywords ─────────────────────────────────