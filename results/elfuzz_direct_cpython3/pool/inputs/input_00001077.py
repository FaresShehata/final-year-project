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
    def wrapped(arg):
        try:
            val = cache[arg]
        except KeyError:
            val = cache.setdefault(arg, fn(arg))
        return val
    return wrapped


# ── Higher order functions & operators ─────────────────────────────────────────

def is_odd(n: int) -> bool:
    return n % 2 == 1


def double_every_other(lst: list[int]) -> list[int]:
    lst[::2] = map(operator.mul, lst[::2], itertools.cycle([2]))
    return lst


def first_last_reversed(lst: list[A]) -> tuple[list[A], bool]:
    """Return the first and last element of `lst`, as well as whether they are equal."""
    fst, lst = lst[0], lst[-1]
    return [fst, lst], fst == lst


def index_of_first_match(
    xs: Iterable[B],
    pred: Callable[[B], bool],
    default: B | None = None,
) -> int | None:
    """Find the index of the first element in iterable satisfying predicate.

    If no such element exists, or if `default` is provided and not found,
    returns None.
    """
    idx = next((i for i, e in enumerate(xs) if pred(e)), None)
    return default if idx is None else idx


def product(factors: Iterable[float]) -> float:
    return functools.reduce(operator.mul, factors)


def sum_iterable(iterable: Iterable[float], initial: float = 0.0) -> float:
    return functools.reduce(operator.add, iterable, initial)


def count_if(pred: Callable[[Any], bool], iterables: Iterable[Any]) -> int:
    return functools.reduce(
        lambda acc, _: acc + 1 if pred(_) else acc,
        iterables,
        0,
    )


def filter_map(func: Callable[[Any], A | None], iterable: Iterable[Any]) -> list[A]:
    return [
        item
        for item in iterable
        if isinstance(item := func(item), A)
    ]


def flatten(iterables: Iterable[Iterable[A]]) -> list[A]:
    return [*itertools.chain.from_iterable(iterables)]


def flatmap(func: Callable[[Any], Iterable[A]], iterable: Iterable[Any]) -> list[A]:
    return [*map(func, iterable)]



# ── Generators ─────────────────────────