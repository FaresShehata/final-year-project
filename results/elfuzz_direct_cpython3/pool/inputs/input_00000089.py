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
    acc._init_value = init  # type: ignore[attr-defined]
    return acc


def make_peepers():
    peepers = []
    for i in range(3):
        peeper = make_accumulator(i+1)
        peepers.append(peeper)
    return peepers


# ── Decorators ────────────────────────────────────────────────────────────────

def trace(func: Callable):
    @functools.wraps(func)
    def traced_func(*args, **kwargs):
        print("->", func.__name__, "(", args, kwargs, ") → ")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise e from None
        else:
            print("<-", result)
            return result
    return traced_func


# ── Higher-order functions & lambdas ──────────────────────────────────────────

def map_iter(iterable: Iterable[A], fn: Callable[[A], B]) -> Iterator[B]:
    for item in iterable:
        yield fn(item)


def map_list(xs: list[A], fn: Callable[[A], B]) -> list[B]:
    return [fn(x) for x in xs]


def filter_iter(iterable: Iterable[A], pred: Callable[[A], bool]) -> Iterator[A]:
    for item in iterable:
        if pred(item):
            yield item


def filter_list(xs: list[A], pred: Callable[[A], bool]) -> list[A]:
    return [x for x in xs if pred(x)]


def reduce_iter(
    iterable: Iterable[A],
    fn: Callable[[A, A], A],
    initial: A | None = None) -> A:

    acc = initial or next(iterable)
    for item in iterable:
        acc = fn(acc, item)
    return acc


def reduce_list(
    xs: list[A],
    fn: Callable[[A, A], A],
    initial: A | None = None) -> A:

    acc = initial or xs[0]
    for item in xs[1:]:
        acc = fn(acc, item)
    return acc


def foldl(fn: Callable, xs: list[Any]) -> Any:
    accum, it = foldr(fn, xs[::-1])
    return accum


def foldr(fn: Callable, xs: list[Any]) -> tuple[Any, Iterator[Any]]:
    head, tail = xs[0], xs[1:]
   is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
