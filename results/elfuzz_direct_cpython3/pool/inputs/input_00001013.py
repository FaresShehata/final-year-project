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

def to_int(n: int) -> int:
    return n


def add_one(x: int) -> int:
    return x + 1


def double(x: int) -> int:
    return x * 2


def cube(x: int) -> int:
    return x ** 3


def increment(x: int) -> int:
    return lambda y: y + 1


def increment_ternary(x: int) -> Callable[[int], int]:
    def increment(y: int) -> int:
        return y + 1

    return increment


class Incrementor():
    def __init__(self):
        self.x = 0

    def __call__(self, y: int) -> int:
        self.x += 1
        return y + 1


def identity(x: int) -> int:
    return x


def inc(x: int) -> int:
    return add_one(identity)(x)


def inc_ternary(x: int) -> Callable[[int], int]:
    def inc(y: int) -> int:
        return add_one(identity(y))(y)

    return inc


def curry(func: Callable[..., B]) -> Callable[[Callable[..., A]], Callable[[A], B]]:
    """Curry a function of arbitrary arity.

    Curry is the process of converting a function with N arguments into a sequence
    of N functions each taking one argument.
    """

    @functools.wraps(func)
    def _curried(*args: A) -> B | None:
        if len(args) >= func.__code__.co_argcount:
            # All args were passed in, so call the original function and get its result.
            return func(*args)
        else:
            # Otherwise create a new function that will be called with all the remaining arguments.
            return lambda *more_args: _curried(*(args + more_args))

    return _curried


@curry
def sum_two(a: int, b: int) -> int:
    return a + b


# ─── Higher-Order Functions ──────────────────────────────────────────────────────


str_len = lambda x: len(str(x))


max_val = lambda xs: max(xs, key=str_len)


def square(x: int) -> int:
    return x ** 2


sum_squares = lambda xs: sum(map(square, xs))


list_map: Callable[[Iterable[A], Callable[[A], B]], list[B]] = lambda xs,divisible_by_five = filter(lambda n: n % 5 == 0, range(10))

# >>> map(lambda s: s.upper(), ['spam', 'eggs', 'sausage']) \
...     == ['SPAM', 'EGGS', 'SAUSAGE']
... 
True

