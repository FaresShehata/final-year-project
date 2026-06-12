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
        rest_items = seq[1:]     # throw away the first item since we've already used it as 'initial'
    else:
        first_item = initial      # use provided 'initial'

    accumulator = first_item

    try:
        for current in seq:
            accumulator = fn(current, accumulator)
    except StopIteration:
        pass
    finally:
        return accumulator


def map(
    fn: Callable[[A], B],
    items: Iterable[A],
) -> Iterator[B]:
    return (fn(item) for item in items)


def zip_longest(
    iterable_a: Iterable[Any],
    iterable_b: Iterable[Any],
    fillvalue: Any = None,
) -> Iterator[tuple[Any, Any]]:
    max_len = max(len(iterable_a), len(iterable_b))
    iterables = [iterable_a, iterable_b]

    while any([next(it, fillvalue) for it in iterables]):
        yield tuple(next((it for it in iterables if next(it, fillvalue)), fillvalue) for it in iterables)



# ── Generators ────────────────────────────────────────────────────────────────

def take(n: int, seq: Iterable[A]) -> Iterator[A]:
    i = 0
    for item in seq:
        if i < n:
            yield item
            i += 1
        else:
            break


def drop(n: int, seq: Iterable[A]) -> Iterator[A]:
    count = n
    for item in seq:
        if count <= 0:
            yield item
        else:
            count -= 1



# ── Itertools ─────────────────────────────────────────────────────────────────

def permutations(iterable: Iterable[Any], r=None) -> Iterator[tuple[Any, ...]]:
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    indices = list(range(n))
    cycles = list(range(n - r + 1, n + 1))[::-1]
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield