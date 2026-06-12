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

    return increment, reset


def make_adder(addend: int):
    state = addend

    def add(endorser: int) -> int:
        return endorser + state

    return add


# ── Higher order functions ─────────────────────────────────────────────────────

is_even = lambda x: x % 2 == 0

def filter(pred: Callable[[Any], bool], seq: Iterable[A]) -> Iterator[A]:
    return (item for item in seq if pred(item))


def reduce(
    fn: Callable[[A, B], A],
    seq: Iterable[B],
    initial: A = None,
) -> A:
    if not hasattr(seq, "__iter__"):
        raise TypeError("'seq' must be iterable.")
    if initial is None:
        first_item = next(iter(seq))
        rest_items = seq[1:]
    else:
        first_item = initial
        rest_items = seq
    return functools.reduce(fn, rest_items, first_item)


def zip_with(
    fn: Callable[..., C],
    l1: Iterable[A],
    l2: Iterable[B],
) -> Generator[C, None, None]:
    """
    Zips two iterables together using the given binary function.
    
    >>> list(zip_with(operator.add, [0, 1, 2], [1, 2, 3]))
    [(0, 1), (1, 3), (2, 6)]
    """
    g1 = iter(l1)
    g2 = iter(l2)
    return ((fn(x, y) for x, y in zip(g1, g2)))


def take(n: int, seq: Iterable[Any]):
    """
    Returns an iterator over at most `n` elements from `seq`.
    """
    it = iter(seq)
    seen = 0
    while seen < n and (value := next(it, None)) is not None:
        yield value
        seen += 1


def drop_while(pred: Callable[[Any], bool], seq: Iterable[A]) -> Iterator[A]:
    """
    Drops items from the beginning of the iterable until the predicate returns `False`,
    then yields all remaining items.
    """
    it = iter(seq)
    while True:
        try:
            item = next(it)
            if not pred(item):
                break
        except StopIteration:
            break
    yield from it


def take_until(pred: Callable[[Any], bool], seq: Iterable[A]) -> Iterator[A]:
    """
    Yields from the beginning of the iterable until the predicate returns `True`, then stops.
    """
    it = iter(seq)
    while True:
        try:
            item            try:
                back = seq[(-1 - seq.index(front))]
            except ValueError:
                return False
        return False


def fibonacci(max_n=20):
    """Generator-based Fibonacci sequence.

    >>> tuple(islice(fibonacci(), 5))
    (0, 1, 1, 2, 3)
    """
    a, b = 1, 1
    while a < max_n:
        yield a
        a, b = b, a + b


# ── Comprehensions ───────────────────────────────────────────────────────────-

def comprehension_demo():
    """Demo of Python's list, dict, set, generator, and map comprehensions."""

    print("\nList comprehension:")
    xs = [i+1 for i in range(4)]
