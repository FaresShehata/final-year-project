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
    return Thunk(_odd_tc, n - 1, acc) if acc else Thunk(_even_tc, n - 1, True)


def even_tc(n: int) -> bool:
    return _even_tc(n, False)


def odd_tc(n: int) -> bool:
    return not even_tc(n)


# ── Higher-order functions, list comprehensions, and generators ───────────────

def map_v1(fn: Callable[[Any], Any], xs: Iterable[Any]) -> list:
    return list(map(fn, xs))


def map_v2(fn: Callable[[Any], Any],
           xs: Iterable[Any]) -> Generator[Any, None, None]:
    yield from (fn(x) for x in xs)


def filter_v1(pred: Callable[[Any], Any],
              xs: Iterable[Any]) -> list:
    return list(filter(pred, xs))


def filter_v2(pred: Callable[[Any], Any],
              xs: Iterable[Any]) -> Generator[Any, None, None]:
    yield from (x for x in xs if pred(x))


def enumerate_v1(xs: Iterable[A]) -> list[tuple[int, A]]:
    return list(enumerate(xs))


def enumerate_v2(xs: Iterable[A],
                 start: int = 0) -> Generator[tuple[int, A], None, None]:
    count = start
    yield from ((count, x) for x in xs)
    count += 1


def accumulate_v1(op: Callable[[B, B], B],
                  initial: B,
                  xs: Iterable[B]) -> list[B]:
    result = []
    current = initial
    for x in xs:
        current = op(current, x)
        result.append(current)
    return result


def accumulate_v2(op: Callable[[B, B], B],
                  initial: B,
                  xs: Iterable[B]) -> Generator[B, None, None]:
    yield initial
    count = 0
    current = initial
    for x in xs:
        current = op(current, x)
        yield current
        count += 1


# ── Generators ────────────────────────────────────────────────────────────────
def gen_fibonacci(maxterm: int) -> Generator[int, None, None]:
    a, b = 0, 1
    while a < maxterm:
        yield a
        a, b = b, a+b


def fibo_gen():
    a, b = 0, 1
    while True:
        yield a
        a,