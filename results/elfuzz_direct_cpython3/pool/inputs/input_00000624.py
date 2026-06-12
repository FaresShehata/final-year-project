"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")


@dataclasses.dataclass(frozen=True)
class Foo:
    bar: int


async def coro():
    pass


def sync_func(a: int) -> str:
    return str(a)


@overload  # Python >= 3.8
def overloaded() -> None:
    ...


@overload
def overloaded() -> bool:
    ...


def overloaded() -> bool:
    if True:
        return False
    else:
        return True


def main() -> None:
    print(unpack_header(b"foo\x00\0\0\0"))
    print(interleave_struct([(69.0, 74.0, 35.0)]))
    print(array_ops())
    print(sync_callables())


print(dataclasses_fields(Foo(bar=5)))


def sleep_and_print(n: int):
    print(f"sleeping {n} seconds")
    time.sleep(n)
    print(f"waking up after sleeping {n} seconds")


# ── generators ────────────────────────────────────────────────────────────────

def count_down(n: int):
    while n > 0:
        yield n
        n -= 1


def generator_expression() -> Generator[int]:
    return (n + 1 for n in range(10))


@overload
def consume(gen: Iterable[object]) -> None:
    ...


@overload
def consume(gen: Iterator[object]) -> object | None:
    ...


def consume(gen):  # type: ignore[misc]  # returns different things depending on whether it's an iterator or not
    try:
        return next(gen)
    except StopIteration as e:
        return e.value


def stream(func: Callable[..., Generator], /, *args):
    gen = func(*args)
    result = consume(gen)
    while result is not None:
        print(result)
        result = consume(gen)


stream(count_down, 5)  # prints from 5 down to 0
stream(generator_expression)  # prints the values yielded by the generator expression


# ── context managers ──────────────────────────────────────────────────────────

async def my_context_manager() -> None:
    await asyncio.sleep(1)
    raise ValueError("a value error")


@contextmanager  # implemented using a class and __enter__/__exit__
class MyContextManager:
    def __init__(self, x: int) -> None:
        self.x = x

    def __enter__(self) -> "MyContextManager":
        print(f"{self.x=} enter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        print(f"{self.x=} exit")
        return True


with MyContextManager(x="hello") as cm:
    print(cm.x == "hello")

async with MyContextManager(x="world") as cm:
    print(cm.x == "world")


try:
    with MyContextManager(x=None):
        raise ValueError("a value error")
except ValueError as e:
    print(e.args[0])


try:
    with my_context_manager():
        raise TypeError("a type error")
except ValueError as e:
    print(e.args[0])

try:
    async with my_context_manager():
        raise TypeError("a type error")
except ValueError as e:
    print(e.args[0])


# ── async generators ──────────────────────────────────────────────────────────

async def async_generator() -> AsyncGenerator[str]:  # type: ignore[type-arg]
    yield "one"
    yield "two"


async def async_stream(func: Callable[..., AsyncGenerator], /, *args):
    async for v in func(*args):
        print(v)


async_stream(async_generator)  # prints one two


# ── coroutines ────────────────────────────────────────────────────────────────

async def future_coroutine() -> str:
    await asyncio.sleep(1)
    return "hello"


def get_future_coroutine() -> Coroutine[str, Any, str]:
    return future_coroutine()


async def run_async_coroutine(coro: Coroutine[Any, Any, str]) -> str:
    return await coro


def call_coroutine(coroutine: Callable[..., Coroutine[Any, Any, str]]) -> str:
    return coroutine()


coro = future_coroutine()
run_async_coroutine(coro)
call_coroutine(get_future_coroutine())

time.sleep(2)


async def launch_task(task: Task) -> None:
    task.start