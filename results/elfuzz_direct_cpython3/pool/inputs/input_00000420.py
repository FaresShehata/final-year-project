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
    def memoized_fn(*args, **kwargs):
        key = (fn.__name__,) + args + tuple(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]

    return memoized_fn


def memoize(fn: Callable) -> Callable:
    """Memoisation decorator using lru_cache from functools."""
    return functools.lru_cache(maxsize=None)(fn)


def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)


factorial_memoised = memoize(factorial)


class Thunk:
    """Helper class for delaying the evaluation of expressions until they are needed."""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def evaluate(self) -> Any:
        try:
            return self.result
        except AttributeError:
            self.result = self.func(*self.args, **self.kwargs)
            return self.result


def fibo_iter(n: int) -> int:
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr


def fibo_gen(n: int) -> Generator[int, None, None]:
    yield from itertools.accumulate(itertools.repeat(None), lambda _, _: next((yield )), initial=(0, 1))[n]


def fibo_rec(n: int) -> int:
    if n < 2:
        return n
    return fibo_rec(n - 1) + fibo_rec(n - 2)


fibos = [
    Thunk(fibo_iter),
    Thunk(fibo_gen),
    Thunk(fibo_rec),
]
for i in range(6): print(i, fibos[i].evaluate())


def nth_fibonacci(n: int) -> int:
    if n < 1:
        raise ValueError('Fibonacchi numbers cannot be negative or zero.')
    return fibo_iter(n).evaluate()


# ── Itertool recipes ──────────────────────────────────────────────────────────<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>
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


