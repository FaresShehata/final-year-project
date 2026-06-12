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
        return None

    def count_until(value: int) -> int:
        while state[0] < value:
            yield state[0]
            state[0] += step

    return dict(
        increment=increment,
        reset=reset,
        count_until=count_until)


def make_adder(step: int = 2) -> Callable[[int], int]:
    def adder(n: int) -> int:
        return n + step
    return adder



# ── Trampoline & tail call optimization ───────────────────────────────────────

def is_tail_call_optimized(function: Callable) -> bool:
    """Check whether function can be optimized with a trampoline.

    See https://wiki.python.org/moin/PythonDecoratorLibrary#Tail_Calls.
    """
    code = function.__code__
    return code.co_flags & 4 == 4 and code.co_stacksize > 0


class TailCall(Exception):
    """Trampoline exception."""


def trampoline(func: Callable) -> Callable:
    """Generate a trampoline to optimize tail calls.

    See https://wiki.python.org/moin/PythonDecoratorLibrary#Tail_Calls.
    """

    @functools.wraps(func)
    def trampolinized(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TailCall as tc:
            return tc.args[0]

    return trampolinized


@trampoline
def factorial(n: int) -> int:
    if not n: raise TailCall(1)
    return n * factorial(n - 1)


@trampoline
def fibonacci(n: int) -> int:
    if n <= 1: return n
    return fibonacci(n - 2) + fibonacci(n - 1)



# ── Itertools ─────────────────────────────────────────────────────────────────

def take(iterable: Iterable[A], n: int) -> list[A]:
    return list(itertools.islice(iterable, n))


def drop(iterable: Iterable[A], n: int) -> list[A]:
    iterable = iter(iterable)
    for i in range(n):
        next(iterable, None)
    return list(iterable)


def nth(iterable: Iterable[A], n: int) -> A | None:
    iterator = iter(iterable)
    for i in range(n):
        next(iterator, None)
    return next(iterator, None)


def count(start: int = 0, step:                "%-50s %7.1f ms" %
                (fn.__qualname__, (after - before) / 1e6),
                file=sys.stderr
            )

    return wrapper


def debug_prints(level: int = 0):
    """Print intermediate values as they are computed."""

    def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            level = max(0, min(len(str(args)), level))
