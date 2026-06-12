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

_even_tc = trampoline(_even_tc)
_odd_tc   = trampoline(_odd_tc)

def even_tc(n: int) -> bool:
    return _even_tc(n, True)


def odd_tc(n: int) -> bool:
    return _odd_tc(n, False)


# ── Higher-order functions ────────────────────────────────────────────────────

def map_func(func: Callable, seq: Sequence) -> list:
    """Implements Python's built-in `map` with a custom implementation."""
    it = iter(seq)
    return [func(item) for item in it]


def filter_func(pred: Callable, seq: Sequence) -> list:
    """Implements Python's built-in `filter` with a custom implementation."""
    it = iter(seq)
    return [item for item in it if pred(item)]


def reduce_func(reducer, initial_value, sequence):
    """Implements Python's built-in `reduce` with a custom implementation."""
    it = iter(sequence)
    try:
        value = next(it)
    except StopIteration as e:
        raise TypeError("Reduce of empty sequence with no initial value") from e
    return functools.reduce(
        reducer,
        (initial_value, value),
        lambda x, y: reducer(x, y))


def accumulate_seq(reducer, initial_value=None, sequence=range):
    """Implements the `accumulate` higher-order function.
    
    >>> accumulate_seq(operator.add, 10, range(5))
    [10, 11, 13, 16, 20]
    """
    it = iter(sequence())
    try:
        first_item = next(it)
        accumulated = initial_value or first_item
        yield accumulated
    except StopIteration as e:
        raise TypeError("Accumulate of empty sequence with no initial value") from e
    try:
        for item in it:
            accumulated = reducer(accumulated, item)
            yield accumulated
    except StopIteration as e:
        raise TypeError("Accumulate of empty sequence with initial value") from e


def compose_func(*funcs: Callable) -> Callable:
    """Compose any number of unary functions into a single function that takes one argument."""
    def composed_func(x):
        return functools.reduce(operator.and_, (f(x) for f in funcs))
    return composed_func


# ── Iterators ────────────────────────────────────────────────────────────────

def take(n: int,