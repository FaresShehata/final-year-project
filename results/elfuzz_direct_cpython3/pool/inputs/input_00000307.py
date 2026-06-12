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


# ── Higher order functions ────────────────────────────────────────────────────

def map_(fn: Callable[[A], B]) -> Callable[[Iterable[A]], list[B]]:
    def inner(iterable: Iterable[A]) -> list[B]:
        return list(map(fn, iterable))
    return inner


def filter_(fn: Callable[[A], bool]) -> Callable[[list[A]], list[A]]:
    def inner(iterable: list[A]) -> list[A]:
        return list(filter(fn, iterable))
    return inner


def take(n: int) -> Callable[[Iterator[Any]], list[Any]]:
    def inner(iterator: Iterator[Any]) -> list[Any]:
        return list(itertools.islice(iterator, n))
    return inner


def drop(n: int) -> Callable[[Iterator[Any]], Iterator[Any]]:
    def inner(iterator: Iterator[Any]) -> Iterator[Any]:
        return itertools.dropwhile(lambda _: _, itertools.islice(iterator, n))
    return inner


def head(iterator: Iterator[A]) -> A | None:
    try:
        first_item = next(iterator)
    except StopIteration:
        return None
    else:
        return first_item


def tail(iterator: Iterator[A]) -> Iterator[A]:
    second_items = iter(next(iterator).__iter__)
    yield from second_items


def zip_(*iterables: Iterable[A]) -> Iterator[tuple[A, ...]]:
    iterators = tuple(itertools.starmap(iter, zip_(*iterables)))
    while True:
        yield tuple(itertools.islice(iterators, len(iterators)))


def unzip(iterpairs: Iterable[tuple[A]]) -> list[list[A]]:
    return list(map(list, zip(*iterpairs)))


def enumerate_(
    iterator: Iterator[A],
    start: int = 0,
) -> Iterator[tuple[int, A]]:
    indexes = itertools.count(start=start)
    return zip(indexes, iterator)


def reverse(iterator: Iterator[A]) -> Iterator[A]:
    items = []
    for item in iterator:
        items.insert(0, item)
    yield from items


def flat_map(fn: Callable[[A], Iterable[B]]) -> Callable[[Iterator[A]], Iterator[B]]:
    def inner(iterator: Iterator[A]):
        for item in iterator:
            yield from fn(item)
    return inner


def flatten(iterable_of_iterables: Iterable[Iterable[A]]) -> Iterator[A]:
    for iterable in iterable_of_iterables:
        yield from