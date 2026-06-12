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
        result = await coroutine
        loop.stop()  # we want to stop after this one iteration
        return result
    except BaseException as e:
        raise


# ── Math utilities ───────────────────────────────────────────────────────────

def average(iterable: Iterable[float]) -> float:
    """Returns the arithmetic mean of iterable's elements."""
    return sum(iterable) / len(iterable)


def median(iterable: Iterable[float]) -> float:
    """Returns the median (middle element) of an iterable sequence of floats."""
    iterator = iter(iterable)
    try:
        values = [next(iterator)]
        for value in iterator:
            bisect.insort(values, value)
        n = len(values)
        return (values[n // 2 - 1] + values[n // 2]) / 2
    except ZeroDivisionError:
        return 0


# ── Structural Pattern Matching ──────────────────────────────────────────────

@runtime_checkable
class MatchProtocol(Protocol[K, V]):
    """Base class for all data structures implementing structural pattern matching."""

    __match_args__: tuple[str]
    def match(self, case: Case) -> V | None:
        ...


@dataclasses.dataclass
class Case(Generic[K, V]):
    descr: str
    predicate: Callable[[K], bool]
    handler: Callable[[K], V]


def match(obj: MatchProtocol[K, V], cases: tuple[Case[K, V]]) -> V | None:
    """Structural pattern matching.

    >>> from dataclasses import dataclass
    >>> from typing import Optional, Union
    >>>
    >>> @dataclass
    ... class Foo:
    ...     bar: int
    ...
    >>> @dataclass
    ... class Bar:
    ...     baz: int
    ...
    >>> obj = Foo(bar=42)
    >>> match(obj, [
    ...     Case('Foo', lambda foo: isinstance(foo, Foo), lambda foo: foo.bar),
    ...     Case('Bar', lambda bar: isinstance(bar, Bar), lambda bar: bar.baz),
    ... ])
    42
    """
    for c in cases:
        if c.predicate(obj):
            return c.handler(obj)
    else:
        return None


# ── Walrus Operator ──────────────────────────────────────────────────────────

def compute_total(x: list[int], acc: int = 0    """

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
