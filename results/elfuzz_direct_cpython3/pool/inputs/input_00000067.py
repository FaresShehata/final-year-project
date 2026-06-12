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
    def wrapped_fn(*args, **kwargs):
        key = args, frozenset(kwargs.items())
        if key in cache:
            return cache[key]
        result = fn(*args, **kwargs)
        if isinstance(result, tuple):
            val, next_ = result
            cache[key] = (val, lambda new_args, new_kwargs: wrapped_fn(
                *next_(new_args), **{**kwargs, **new_kwargs},
            ))
        else:
            cache[key] = result
        return result
    return wrapped_fn



# ── Higher-order functions & combinators ───────────────────────────────────────

def identity(x: A) -> A:
    return x


def invoker(funcs: list[Callable]) -> Callable[..., Any]:
    """Invoker combinator, creates a callable from a list of function arguments.

    >>> invoker([lambda x: x+1])(5)
    6
    """
    def invoked(*args, **kwargs):
        results = map(lambda func: func(*args, **kwargs), funcs)
        return sum(results, start=identity)
    return invoked


def compose2(f: Callable, g: Callable) -> Callable:
    """Composes two unary functions using the given order.

    >>> compose2(lambda x: x*x, lambda y: y*y)(3)
    9
    """
    def composed(*args, **kwargs):
        return f(g(*args, **kwargs))   # type: ignore[misc]
    return composed


def flip(func: Callable) -> Callable:
    """Flips the argument order of a binary function.
    
    >>> flip(lambda x,y: x+y)(4, 5)
    9
    """
    flipped = lambda a,b: func(b,a)
    flipped.__name__ = func.__name__    # type: ignore[attr-defined]
    flipped.__doc__ = func.__doc__      # type: ignore[attr-defined]
    return flipped


def const(val: Any) -> Callable:
    """Returns an unary function which always returns the same value."""
    def func(_: Any) -> Any:
        return val
    return func


def nth_element(index: int, iterable: Iterable[A]) -> A:
    """Return the nth element from an iterable."""
    iterator = iter(iterable)
    try:
        for i in range(index):
            next(iterator)
        return next(iterator)
    except StopIteration:
        raise ValueError(f"Index {index}            result = result.fn(*result.args)
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


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
