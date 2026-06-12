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

print(add3(1)(2)(3)) # 6

@curry
def mul3(a: int, b: int, c: int) -> int:
    return a * b * c

print(mul3(1)(2)(3)) # 6


# ── Partial application example from StackOverflow ────────────────────────────

class WrapPartialFunction:
    """
    A class that wraps the `partial` method and also allows the use of `*` to pass arguments.
    
    Example usage:
        >>> wrap_partial_function = WrapPartialFunction()
        >>> wrapped_add = wrap_partial_function.partial(operator.add, 5)
        >>> print(wrapped_add(10))  # Output: 15
        >>> print(wrap_partial_function(5)(*range(10)))  # Output: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
        
    Note: The wrapper can only be used once per instance due to limitations with Python's type system.
    """

    def __init__(self):
        self.funcs = []

    def __call__(self, *args):
        return lambda func: self._add_func(func, *args)

    def partial(self, func, *args):
        return self._add_func(func, *args)

    def _add_func(self, func, *args):
        self.funcs.append((func, args))
        return lambda *more_args: self._apply_funcs(*more_args)

    def _apply_funcs(self, *args):
        for func, argset in reversed(self.funcs):
            args = list(argset) + list(args)
        return func(*args)


wrap_partial_function = WrapPartialFunction()

wrapped_add = wrap_partial_function.operator.add(5)
print(wrapped_add(10))  # Output: 15

print(wrap_partial_function(5)(*range(10)))  # Output: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]

# ── Trampolining example from StackOverflow ───────────────────────────────────

def do_something_with_trampolining():
    def inner(value):
        nonlocal counter
        counter += 1
        return