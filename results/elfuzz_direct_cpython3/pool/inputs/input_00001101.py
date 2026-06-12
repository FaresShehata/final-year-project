"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Set
from dataclasses import dataclass, field
from functools import partial
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from itertools import chain, cycle, dropwhile, groupby, tee
from types import GeneratorType, UnionType
from types import ModuleType as _ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    overload,
    runtime_checkable,
)


T = TypeVar("T")
U = TypeVar("U")


# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(str, enum.Enum):
    PENDING         = "pending"
    RUNNING         = "running"
    COMPLETED       = "completed"
    FAILED          = "failed"
    CANCELLED_BY_US = "cancelled by us"


@dataclass(frozen=True)
class Result(Awaitable[T]):
    status: Status     = field(compare=False, default=Status.PENDING)
    value: T           = field(default=None, compare=False)

    def __post_init__(self):
        if self.status == Status.FAILED:
            raise ValueError(self.value)

    @property
    def done(self) -> bool:
        return self.status in (Status.COMPLETED, Status.FAILED)

    def __bool__(self) -> bool:
        return not self.done


def run_coro(coro: Coroutine[None, None, T], timeout: float | None = None) -> T:
    """
    Run a coroutine and get its result.

    Args:
        coro: The coroutine to run.
        timeout: Maximum time to wait for the coroutine to finish.

    Returns:
        The result of the coroutine.

    Raises:
        TimeoutError: If the coroutine does not finish within the given timeout.
    """

    # Create an event loop and run the coroutine
    loop = asyncio.get_event_loop()
    try:
        future = loop.create_future()
        future.set_result(coro.send(None))
        future.add_done_callback(lambda _: loop.stop())
        if timeout is not None:
            loop.call_later(timeout, lambda _: future.cancel())
        loop.run_forever()

        # Check if the coroutine was cancelled
        if future.cancelled():
            raise RuntimeError("Coroutine was cancelled")

        # Get the result of the coroutine
        result = future.result()

        # Raise an error if the coroutine failed
        if isinstance(result, Exception):
            raise result from None

        return result

    finally:
        loop.close()


# ─── Async generators ─────────────────────────────────────────────────────────


async def first(iterable: Iterable[T]) -> T:
    """Return the first element of an iterable."""

    return next(iter(iterable))


async def last(iterable: Iterable[T]) -> T:
    """Return the last element of an iterable."""

    iterator = iter(iterable)
    while True:
        item = next(iterator, None)
        if item is None:
            break
        yield item


async def take(iterable: Iterable[T], n: int) -> Iterable[T]:
    """Take the first `n` elements of an iterable."""

    return [item async for