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


def split_pipe(f: Callable[[int], int]) -> tuple[Callable, Callable]:
    """Split a function into two pipelines."""

    # In Python, we can't use `pipe` to define the inverse of `compose`,
    # so we'll write it manually.
    def inv_f(arg):
        while arg != 0 and arg != 1:
            arg -= 1
            yield arg
            arg += 1
        yield arg

    def rev_inv_f(f_args):
        for arg in inv_f(*f_args):
            yield arg

    def piped(f_args):
        return pipe(rev_inv_f)(
            fmap(f),
            map(int),
            list
        )

    def inverted(f_args):
        return pipe(
            map(float),
            list,
            rev_map(inv_f),
            fmap(f),
            list
        )

    return piped, inverted


def check_curries():
    assert curry(add3)(2, 6, 9) == 17
    assert curry(add3)(2, 6)(9) == 17
    assert curry(add3)(2)(6, 9) == 17
    assert curry(add3)(2)(6)(9) == 17
    assert curry(compose)(add3)(5, 8, 2) == 15
    assert curry(pipe)(add3)(2, 6, 9) == 17
    assert curry(pipe)(add3)(2, 6)(9) == 17
    assert curry(pipe)(add3)(2)(6, 9) == 17
    assert curry(pipe)(add3)(2)(6)(9) == 17
    assert curry(pipe)(pipe)(add3)(2, 6, 9) == 17
    assert curry(split_pipe)(add3)[-1]([2, 6, 9]) == [17]
    assert curry(split_pipe)(add3)[0](list(range(2)))[-1]() == [2, 6, 9]


check_curries()


# ── Trampoline example ───────────────────────────────────────────────────────

class Thunk:
    def __init__(self, func, *args):
        self._func = func
        self._args = args

    def __iter__(self):
        return self

    def __next__(self):
        try

def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc ^ True)

assert EVEN == even_tc(42), "EVEN is wrong"
assert ODD == odd_tc(42), "ODD is wrong"

EVEN = TRUE(IF(EVEN)(_even_tc, FALSE))(TRUE)
ODD  = NOT(EVEN)

def fib_rec(n: int) -> int:
    if n <= 2:
