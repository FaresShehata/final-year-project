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


# ── Partial application with Python's `*` and `**` operators ────────────────

def sum_all(xs: list[int]) -> int:
    return sum(xs)


sum_square = sum_all.__func__(lambda x: x ** 2)


def apply_twice(f: Callable[[int], int], x: int) -> int:
    return f(f(x))


apply_twice_sum = apply_twice(sum_all)


test_apply_twice = """
>>> sum_all([1, 2, 3]) == apply_twice_sum((1, 2, 3))
True
"""


# ── Combinator combinators ───────────────────────────────────────────────────

def id_(x: A) -> A:
    return x


def compose_func(g: Callable[A, B], f: Callable[B, C]) -> Callable[A, C]:
    return lambda x: g(f(x))


def mul_2_and_add_5(x: int) -> int:
    return 2*x + 5


def is_even(z: int) -> bool:
    return z % 2 == 0


test_compose = """
>>> compose(is_even, mul_2_and_add_5)(7)
False
"""

test_curry = """
>>> add3(1)(2)(3)
6
"""


# ── Trampoline implementation ────────────────────────────────────────────────

class Trampoline(Exception): pass
class Done(object): pass

def trampoline(func: Callable[..., object]) -> Callable[..., object]:
    """
    Makes sure that recursive calls to the given function are implemented as trampolines.
    
    This allows for very deep recursion without exhausting the stack.

    Note that this decorator works best when used on tail-recursive functions.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs) -> object:
        try:
            while True:
                res = func(*args, **kwargs)
                if isinstance(res, Trampoline):
                    args = res.args
                    kwargs = res.kwargs
                elif isinstance(res, Done):
                    break
                else:
                    raise ValueError("invalid trampoline state", res)
        except RecursionError:
            print("Recursion limit exceeded!", file=sys.stderr)
            raise
        return res.value
    
    return inner


@trampoline
def factorial(n: int) -> int | Trampoline[int]:
    assert n