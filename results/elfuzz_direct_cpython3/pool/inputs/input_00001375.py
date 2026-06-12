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

func(key="something else")


# ── Unpack kwargs into named args ────────────────────────────────────────────

def unpack_kwargs(**kwargs) -> None:
    bar = kwargs["bar"]

unpack_kwargs(foo=1, bar=2)


# ── Context manager with subcontext manager ──────────────────────────────────

with open("file.txt", mode="rt") as file:
    with contextlib.redirect_stdout(file) as f:
        print("Hello world!")


# ── Suppress context manager ─────────────────────────────────────────────────

contextlib.suppress(TypeError)(lambda: "foo" + 10)


# ── Timeout context manager ─────────────────────────────────────────────────

contextlib.timeout(3)(lambda: "foo" + 10)


# ── Redirect stdout (and stderr) to a file ───────────────────────────────────

contextlib.redirect_stdout(io.StringIO())()


# ── Typing Extras ───────────────────────────────────────────────────────────

Annotated[int, "I'm an annotation"]


def foo(bar: Annotated[int, "I'm the type"]) -> Annotated[int, "I'm the return"]:
    ...


reveal_type(Annotated[int, "I'm an annotation"])


type_hint_with_annotation = Annotated[int, "I'm the type hint"]


reveal_type(typehint_with_annotation)


TypeAlias = Annotated[int, "I'm a type alias"]


AsyncIterable[A]: TypeAlias = AsyncIterator[A] | Awaitable[AsyncIterator[A]]


# ── Get type hints ──────────────────────────────────────────────────────────

print(get_type_hints(my_coroutine))


# ── Reveal type (stub function) ─────────────────────────────────────────────

def typed_dict_example(foo: UserRecord) -> None:
    bar = foo['id']

typed_dict_example(UserRecord(id=1, name='John', email='john@example.com'))


# ── Never ──────────────────────────────────────────────────────────────────

never_value: Never = never_value


# ── Annotated ───────────────────────────────────────────────────────────────

annotated_int: Annotated[int, "This is an annotation"] = 10


# ── ParamSpec ───────────────────────────────────────────────────────────────

F = ParamSpec('F')


def takes_any_function(func: F) -> None:
    pass


