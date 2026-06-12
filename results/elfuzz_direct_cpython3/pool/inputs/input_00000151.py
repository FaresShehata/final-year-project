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

    def apply(self):
        return self.fn(*self.args)


def trampoline(thunk: Thunk) -> Any:
    while isinstance(thunk, Thunk):
        thunk = thunk.apply()
    return thunk


def delay(func: Callable) -> Thunk:
    return Thunk(func)


def lazy_adder(a: int, b: int) -> Thunk:
    return Thunk(add, a, b)


# ── Partial applications and lambdas ──────────────────────────────────────────

def partial(func: Callable, *positional_args: A) -> Callable:
    """
    Return a new callable with the given positional arguments pre-applied.

    >>> double = partial(operator.mul, 2)
    >>> triple = partial(operator.mul, 3)
    >>> square = partial(pow, 2)
    """

    def wrapped(*rest):
        return func(*positional_args, *rest)

    return wrapped


def lambda_factory(fn: Callable) -> Callable:
    """
    Create a lambda from the given function by capturing any free variables.
    """

    try:
        closure_vars = fn.__closure__ or ()
    except AttributeError:
        raise ValueError(
            "This utility will only work on pure functions without side-effects"
        )
    else:
        closure_vars = {var.cell_contents for var in closure_vars}
        captured_variables = {
            name: value for name, value in locals().items() if value in closure_vars
        }
        return eval(f"lambda {', '.join(captured_variables.keys())}: {fn!s}", globals(), captured_variables)


# ── Higher-order functions ────────────────────────────────────────────────────

def map_itover(fn: Callable, seq: Iterable[A]) -> Iterator[B]:
    for item in seq:
        yield fn(item)


def filter_it(seq: Iterable[A], predicate: Callable[[A], bool]) -> Iterator[A]:
    for item in seq:
        if predicate(item):
            yield item


def zip_it(left_seq: Iterable[A], right_seq: Iterable[B]) -> Iterator[tuple[A, B]]:
    left_iterable = iter(left_seq)
    right_iterable = iter(right_seq)
    while True:
        try:
            left_item = next(left_iterable)
            right_item = next(right_iterable)
        except StopIteration:
            break
        else:
            yield left_item, right_item
    raise ValueError("Unequal lengths")


def reduce