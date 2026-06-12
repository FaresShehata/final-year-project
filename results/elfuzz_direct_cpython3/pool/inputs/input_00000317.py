"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
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


# ── Iterators & generators ────────────────────────────────────────────────────

def fib(n: int) -> Iterable[int]:              # generator expression
    a, b = 0, 1
    while a <= n:
        yield a                               # yields the current value of 'a' back to caller
        a, b = b, a+b                         # updates 'a' with the next Fibonacci number


def map_iter(func: Callable, iterable: Iterable[A]) -> Iterable[B]:
    """Implements an iterator version of func's built-in counterpart."""
    for item in iterable:
        yield func(item)


def filter_iter(func: Callable, iterable: Iterable[A]) -> Iterable[A]:
    """Implements an iterator version of func's built-in counterpart."""
    for item in iterable:
        if func(item):     # could also be written `if func(item) is True`
            yield item


def take(iterable: Iterable[A], n: int) -> Generator[A, A, None]:
    """Returns the first N items from the provided iterable object."""
    for i, item in enumerate(iterable):
        if i >= n:
            break
        yield item


def drop(iterable: Iterable[A], n: int) -> Generator[A, None, None]:
    """Removes the first N items from the provided iterable object."""
    for i, item in enumerate(iterable):
        if i >= n:
            yield item


def nth(iterable: Iterable[A], n: int) -> A | None:
    """Return the nth element of the given iterable; otherwise, return None."""
    try:
        return next(itertools.islice(iterable, n, None))  # type: ignore[misc]
    except StopIteration:
        return None


def zip_longest(*iterables: Iterable[Any]) -> Generator[tuple, tuple, None]:
    sentinel = object()
    iterators = [iter(it) for it in iterables]
    while iterators:
        values = []
        for itr in iterators:
            try:
                val = next(itr)
            except StopIteration:
                val = sentinel
            values.append(val)
        if all(val is sentinel for val in values):
            raise ValueError("All input sequences are exhausted.")
        yield tuple(value for value in values if value is not sentinel)


# ── High-order functions ──────────────────────────────────────────────────────

def apply(f: Callable[..., B], /, *args: A, **    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

