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


# ── Positional-only arguments ────────────────────────────────────────────────

def func(pos_only, /, pos_or_kwd, *, kwd_only) -> None:
    pass


# ── Overloading functions with the same name but different parameter types ────

def f(a: int | float): ...
def f(b: complex) -> None: ...

f(1) # OK, both signatures match
f(1j) # OK, second signature matches
f(1.0) # OK, first signature matches
f(True) # ERROR, no matching function found


# ── Using types as type hints ────────────────────────────────────────────────

if isinstance(x, int):
    if not callable(getattr(x, "__abs__", None)):
        raise TypeError(f"{type(x).__name__} object is not callable")

if isinstance(x, (str, bytes)):
    pass

if isinstance(x, numbers.Real):
    pass


# ── Using Union and Optional aliases to represent union types ────────────────

from typing import Union, Optional

x: Union[int, str] = 123
y: Optional[str] = None
z: Union[int, str, None] = "abc"


# ── Using Callable alias to represent function types ────────────────────────

def add_one(x: int) -> int:
    return x + 1

add_one: Callable[[int], int]


# ── Using Protocol to define custom type hints ───────────────────────────────

from typing import Protocol

class MyProtocol(Protocol):

    def foo(self) -> str:
        ...


class MyClass:

    def bar(self, x: int) -> None:
        pass

    def baz(self) -> None:
        pass

my_class: MyProtocol

my_class = MyClass()

my_class.bar(123)


# ── Using TypeVar to define generic types ───────────────────────────────────

V = TypeVar("V")

def foo(v: V) -> V:
    return v

foo(123)


# ── Defining type variables using ParamSpec ──────────────────────────────────

ParamStr = ParamSpec("ParamStr")
def concat(*, s: str, sep: str = "", *args: ParamStr.V