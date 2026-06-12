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
    task = loop.create_task(coro)
    task.add_done_callback(lambda _: loop.stop())
    await task


async def fully_run_async_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Waits until all tasks have been cancelled and then stops the event loop.

    This function is useful when you want to ensure that all pending tasks have completed before stopping the event loop.

    Args:
      loop: Event loop.

    Examples:

        from src.utils.async_utils import fully_run_async_loop

        async def main() -> None:
            ...

        loop = asyncio.get_event_loop()

        loop.create_task(main())  # Start the coroutine in a separate task
        await fully_run_async_loop(loop)  # Wait until all tasks have finished


    """

    while loop.is_running():
        await asyncio.sleep(0.        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
