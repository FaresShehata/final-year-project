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

    return increment, reset, peek


incr, reset, peek = make_counter()

print(f"Counter's value: {peek()}")
reset()
print(f"Incrementing once: {incr()}")
print(f"Incrementing again: {incr()}")
print(f"Incrementing after reset: {incr()}")


# ── Higher order functions ─────────────────────────────────────────────────────

def times(fn: Callable[[Any], Any], i: int) -> Iterable[Any]:
    while i > 0:
        yield fn(i)
        i -= 1


def sum_of_squares(nums: Iterable[int]) -> int:
    return sum(num ** 2 for num in nums)


print(sum_of_squares([1, 2, 3]))


def take_while(pred: Callable[[int], bool], nums: Iterable[int]):
    for x in nums:
        if not pred(x): break
        yield x


print(list(take_while(lambda x: x < 5, range(5))))


def repeat(func: Callable, times: int) -> Callable:
    """Create a new "repeating" function which calls the given one `times` times."""
    assert times > 0
    def repeating(*args, **kwargs):
        for _ in range(times - 1):
            func(*args, **kwargs)
        return func(*args, **kwargs)
    return repeating


def memoize(func: Callable) -> Callable:
    cache = {}
    @functools.wraps(func)
    def memoized(*args):
        if args in cache:
            return cache[args]
        else:
            val = func(*args)
            cache[args] = val
            return val
    return memoized


@memoize
def fibo(n: int) -> int:
    if n <= 1: return n
    return fibo(n-1) + fibo(n-2)


def fibonacci_series():
    for n in itertools.count(0):
        yield fibo(n)


fibos = fibonacci_series()


# ── Generators ────────────────────────────────────────────────────────────────

class FibonacciIterator:
    """Generator version of fibonacci series."""

    def __init__(self, max_iter=None):
        self.max_iter = max_iter
        self.a = self.b = 1
        self.iteration_count = 0

    def next(self) -> int:
