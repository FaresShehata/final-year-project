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
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


# ── Asyncio utils ────────────────────────────────────────────────────────────

async def run_until_complete(
    loop: asyncio.AbstractEventLoop,
    coroutine: Awaitable[T],
) -> T:
    """Runs the given coroutine and returns its value. The method uses a blocking call to ensure any exceptions raised are propagated back.

    Args:
      loop: Event loop.
      coroutine: Coroutine object to be executed.

    Returns:
      Return value of the coroutine.

    Raises:
      Any exception raised by the coroutine or `loop.run_forever()`.

    """
    try:
        await coroutine
    except Exception as e:
        raise e from None


async def wrap_with_context_manager(loop: asyncio.AbstractEventLoop, coro: Awaitable[T]) -> T:
    """Wraps an event loop with a context manager for easier error handling.

    Args:
      loop: Event loop.
      coro: Coroutine object to be executed.

    Returns:
      Return value of the coroutine.

    Raises:
      Any exception raised by the coroutine or `loop.run_forever()`.

    """

    async with loop.create_task(coro) as task:
        if task.exception():
            raise task.exception()
        else:
            return task.result()


async def run_coroutine_in_background(loop: asyncio.AbstractEventLoop, coro: Awaitable[T]) -> T:
    """Starts a new background thread to run the given coroutine asynchronously.

    Args:
      loop: Event loop.
      coro: Coroutine object to be executed.

    Returns:
      Return value of the coroutine.

    Raises:
      Any exception raised by the coroutine or `loop.run_forever()`.
    """

    future = loop.run_in_executor(None, lambda: run_with_exception_logging(wrap_with_context_manager, (loop, coro)))
    result = await future
    return result


def run_with_exception_logging(func: Callable[[], Awaitable[T]]) -> T:
    """Helper function that runs a coroutine and logs any exception it raises.

    Args:
      func: Function to execute.

    Returns:
      Result of the coroutine.

    Raises:
      Any exception raised by the coroutine or `func`.

    """

    try:
        return func()
    except Exception as exc:
        print(f"Exception thrown while executing coroutine: {exc}")
        raise

# ── Data classes ─────────────────────────────────────────────────────────────-

@dataclasses.dataclass(slots=True)
class ImageData:
    url: str
    height: int
    width: int
    format: str
    size: int

    @classmethod
    def from_json(cls, json_data: dict[str, V]) -> ImageData:
        return cls(**json_data)


# ── Generics ─────────────────────────────────────────────────────────────────-

@runtime_checkable
class MyProtocol(Protocol[K]):
    """Simple protocol."""

    k: K
    v: K | None
    f: Callable[[K], V]

    def __init__(self, key: K) -> None:
        ...

    @overload
    def foo(self, n: int) -> None:
        ...

    @overload
    def foo(self, s: str) -> None:
        ...

    def foo(self, x: int | str) -> None:
        ...


def my_function(a: MyProtocol[int]) -> None:
    """This function accepts only objects which implement the MyProtocol protocol."""


class Foo(MyProtocol[float]):
    def __init__(self, k: float) -> None:
        self.k = k
        self.v = k * 10
        self.f = lambda k: int(k + 5.34)


class Bar(MyProtocol[float]):
    v: float | None
    f: Callable[[float], float]
    g: list[float]


my_foo = Foo(5.6789)

print(my_foo.foo("hello"))
print(my_foo.foo(5))

try:
    bar = Bar(1.2345)
except TypeError as err:
    print(err)



# ──