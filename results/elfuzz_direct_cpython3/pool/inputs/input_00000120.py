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
    cache = {}

    @functools.wraps(fn)
    def inner(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = rv = fn(*args)
            return rv
        except TypeError:
            return fn(*args)

    return inner


# ── Higher-order functions & generators ────────────────────────────────────────

def map2(fn: Callable[[A, B], C], xs: Iterable[A], ys: Iterable[B]) -> Generator[C, None, None]:
    """Like `map` but returns a generator instead of a list."""
    for x, y in zip(xs, ys):
        yield fn(x, y)


def filter2(pred: Callable[[A], bool], xs: Iterable[A]) -> Generator[A, None, None]:
    """Like `filter` but returns a generator instead of a list."""
    for x in xs:
        if pred(x): yield x


def reduce2(
        fn: Callable[[A, B], A],
        xs: Iterable[A],
        identity: A,
    ) -> A:
    """Reduce a sequence to a single value using a binary operation."""
    it = iter(xs)
    accum = next(it)
    for elem in it:
        accum = fn(accum, elem)
    return accum


def scanl2(
        fn: Callable[[A, B], A],
        xs: Iterable[A],
        identity: A,
    ) -> Generator[A, None, None]:
    """Like `scanl`, but the final element is included as well."""
    it = iter(xs)
    accum = next(it)
    yield accum
    for elem in it:
        accum = fn(accum, elem)
        yield accum


def take_while2(pred: Callable[[A], bool], xs: Iterable[A]) -> Generator[A, None, None]:
    """Take elements from an iterable while a predicate holds true."""
    for x in xs:
        if not pred(x): break
        yield x


def drop_while2(pred: Callable[[A], bool], xs: Iterable[A]) -> Generator[A, None, None]:
    """Drop elements from an iterable while a predicate holds true."""
    it = iter(xs)
    for x in it:
        if pred(x): continue
        yield x
        break
    yield from it


def repeat(n: int) -> Callable[[], int]:
    """Generate integers indefinitely and then stop after n iterations."""
    i =