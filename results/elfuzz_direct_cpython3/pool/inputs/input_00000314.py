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


def filter_map(some_fn: Callable[[Any], bool | None],
               another_fn: Callable[[Any], T]) -> Callable[[Sequence[T]], Set[T]]:
    """
    Given two functions, `some_fn` and `another_fn`, returns a callable that takes
    an iterable of values and returns the set resulting from applying `some_fn`
    to each value and filtering out those for which `another_fn` returns `None`.
    """

    def filtered_set(iterable: Sequence[T]) -> Set[T]:
        return {another_fn(value) for value in iterable if some_fn(value)}

    return filtered_set


def run_pipeline():
    print(
        "===== PIPELINE =====\n"
        ">>> [2, 4, 6].pipe(add3).map(int_to_church)\n"
        "===> {'8', '12'}\n\n"
        ">>> [2, 4, 6].pipe(map(str)).filter(bool).fold_str(', ', '', '')\n"
        "===> '2, 4, 6'\n"
    )


# ── Partial application using currying ────────────────────────────────────────

def foo1(a: int, b: int, c: int): pass
foo1_ = curry(foo1)


def foo2(a: int, b: int, c: int, d: int): pass
foo2_ = curry(foo2)


def bar():
    print(
        "===== PARTIAL APPLICATION USING CURRYING =====\n"
        ">>> foo1_(b=5)(1, 2)\n"
        "===> <function foo1 at 0x7f9d7a2c3e60>\n"
        "\n"
        ">>> foo2_(2)(3)(4)(5)\n"
        "===> 15\n"
    )


# ── Partial application using functools.partial ──────────────────────────────

def baz1(a: int, b: int, c: int): pass
baz1_ = functools.partial(baz1, b=5)


def baz2(a: int, b: int, c: int, d: int): pass
baz2_ = functools.partial(baz2, c=3)


def test_partial_application():
    print(
        "===== PARTIAL APPLICATION USING FUNCTOOLS.PARTIAL =====\n"
        ">>> baz2