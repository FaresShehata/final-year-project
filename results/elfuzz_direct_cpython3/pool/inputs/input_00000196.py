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
    """Accumulate and average a sequence of numbers."""

    total = init
    count = 0

    def accumulate(value: float) -> float:
        nonlocal total, count
        total = total + value
        count = count + 1
        return total / count

    return accumulate


# ── Partial application with variables as parameters ───────────────────────────

def take_n(func: Callable, n: int) -> Callable[[Iterable[A]], list[B]]:
    """Generate the first N results from a unary function over iterables."""
    return lambda iterable: list(itertools.islice(map(func, iterable), n))


def is_odd_count(items: Iterable[int]) -> bool:
    return sum(map(bool, filter(operator.not_, items))) % 2 != 0


# ── Higher-order functions & lambdas ───────────────────────────────────────────

def inc(lazy_func: Callable[[int], int]) -> Callable[[int], int]:
    """Increment by one."""
    return lazy_func(lazy_func)


def take_5(lazy_func: Callable[[int], int]) -> Callable[[int], int]:
    """Take five values."""
    return lazy_func(lazy_func(lazy_func))



# ── Trampolines ───────────────────────────────────────────────────────────────


class TrampolineError(Exception): pass

class Thunk:
    "Thunking wrapper around a computation."
    
    def __init__(self, thunk, *args, **kwargs):
        self.thunk = thunk
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self):
        try:
            val = self.thunk(*self.args, **self.kwargs)
        except TrampolineError as e:
            raise e
        else:
            if isinstance(val, Thunk):
                return val()
            elif callable(val):
                return Thunk(val)
            return val

    def __repr__(self):
        return repr(self())  # __str__, __repr__ are not necessarily equivalent.


def trampoline(thunk: Thunk) -> Any:
    """Trampoline for a thunk that returns another thunk or a value."""
    while isinstance(thunk, Thunk):
        thunk = thunk()
    return thunk<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>

is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
