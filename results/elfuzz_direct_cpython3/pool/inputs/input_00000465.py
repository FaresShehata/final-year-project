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


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()

    def __or__(self, other: Flag) -> Flag:
        return Flag(sum(map(int, (self.value, other.value))))


# ── Functions ────────────────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    """Add two integers."""

    # Check input types and raise TypeError
    assert isinstance(a, int), "a must be an integer"
    assert isinstance(b, int), "b must be an integer"

    # Perform addition
    return a + b


async def add_async(a: int, b: int) -> int:
    """Asynchronously add two integers.

    This function returns an awaitable object representing the future result of
    the addition operation. The actual addition computation is performed by the
    event loop using the asyncio library's scheduling mechanism.
    """

    # Check input types and raise TypeError
    assert isinstance(a, int), "a must be an integer"
    assert isinstance(b, int), "b must be an integer"

    # Schedule the addition task asynchronously
    return await asyncio.ensure_future(add_task(a, b))


async def add_task(a: int, b: int) -> int:
    return a + b


def sum_of_squares(nums: list[int]) -> int:
    total = 0
    for num in nums:
        total += num**2
    return total


def filter_odd(numbers: Iterable[int]) -> List[int]:
    return list(filter(lambda x: x % 2 == 0, numbers))


def map_plus_one(numbers: Iterable[int]) -> list[int]:
    return list(map(lambda x: x + 1, numbers))


def double_and_sort(numbers: Iterable[int]) -> list[int]:
    return sorted(list(map(lambda x: 2 * x, numbers)))


def sum_prefixes(nums: Iterable[int]) -> List[int]:
    prefix_sum = 0
    results = []

    for num in nums:
        prefix_sum += num
        results.append(prefix_sum)

    return results


def get_unique_nums(nums: Iterable[int]) -> Set[int]:
    seen = set()
    unique_nums = []

    for num in nums:
        if num not in seen:
            seen.add(num)
            unique_nums.append(num)

    return unique_nums


def find_max_bfs(graph: Graph) -> int:
    visited = set()
    max_val = -mathONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
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


# ── Decorators ───────────────────────────────────────────────────────────────

def trace(func: Callable[..., T]) -> Callable[..., T]:
    """
    Prints the function signature and return value when called.
    """

    @functools.wraps(func)
    def wrapper_trace(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
