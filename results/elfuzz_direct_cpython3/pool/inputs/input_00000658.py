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


def make_generator():
    state = []

    def append(v):
        state.append(v)

    def pop():
        try:
            return state.pop()
        except IndexError:
            raise StopIteration

    yield append
    yield pop


# ─────────────────────────────────────────────────────────────────────────────


# ── Trampolines ──────────────────────────────────────────────────────────────

def trampoline(fn: Callable) -> Callable:
    """Trampolines are used to avoid stack overflow errors caused by recursive calls.

    A trampoline transforms the recursively-nested call of `fn` into one that can be properly
    unwound instead.
    """

    @functools.wraps(fn)
    def trampolined(*args, **kwargs):
        while True:
            res = fn(*args, **kwargs)
            if isinstance(res, tuple) and res[0] == "trampoline":
                args = res[1:]
            else:
                return res
    return trampolined

@trampoline
def fib_trampolined(n: int) -> int:
    if n < 2:
        return n
    return fib_trampolined(n - 1) + fib_trampolined(n - 2)

fib_trampolined.cache_clear()

def fib_iterative(n: int) -> int:
    if n < 2:
        return n
    a, b = 0, 1
    for i in range(n-1):
        a, b = b, a+b
    return b


# ─── Higher order functions ───────────────────────────────────────────────────

def map_by_index(fn: Callable[[int, A], B],
                 xs: list[A]) -> list[B]:
    return [fn(i,x) for i, x in enumerate(xs)]


def map_by_index_with_indices(fn: Callable[[int, A, int], B],
                              xs: list[A]) -> list[B]:
    return [fn(i,x,i) for i, x in enumerate(xs)]


def filter_by_predicate(pred: Callable[[int, A], bool],
                        xs: list[A]) -> list[A]:
    return [x for i, x in enumerate(xs) if pred(i, x)]


def filter_by_predicate_and_removal(pred: Callable[[int, A], bool],
                                    xs: list[A]) -> list[A]:
    return [x for i, x in enumerate(xs) if not pred(i, x)]


def zip_map_fn((a,b): A,B) -> tuple[int,A,B]:
    return a + b

def zip_map_fn_2((a,b): A,B) -> tuple[str,str]:
    return f'{a}-{b}'

def zip_map_fn_3((a,b,c): A,B,C) -> tuple[int,int,int]:
    return (a + b, b + c, c + a)



def zip_map_by_indexes(fn: Callable[[int, A, int, B], C],
                       xs: list[A],
                       ys: list[B]) -> list[C]:
    return [fn(i,a,i+1,b) for i, (a, b) in enumerate(zip(xs, ys))]


def zip_map_by_values(fn: Callable[[A, B], C],
                      xs: list[A],
                      ys: list[B]) -> list[C]:
    return [fn(a,b) for a, b in zip(xs, ys)]


def flatmap_by_indexes(fn                message = f'{len(excs)} exceptions occurred during execution'
            super().__init__(excs)

            self.context = context or {}
            self.exceptions = excs

        def __str__(self) -> str:
            lines = [
                super().__str__()
            ]
            lines.extend(e.__str__() + '\n' for e in self.exceptions)
            return ''.join(lines)


def raise_if(
        condition: bool,
        msg: str | None = None,
        exc: type[BaseException] = ValueError
) -> None:
    if condition:
        raise exc(msg)


def raise_if_not(
        condition: bool,
        msg: str | None = None,
