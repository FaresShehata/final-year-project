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


add2 = compose(add3, lambda a: a - 2)


def partial(func: Callable, /, *bound_args: A, **bound_kwargs: B) -> Callable:
    """Partial application of an arbitrary number of positional and keyword arguments to a callable.
    
    The _partial_ decorator is also implemented as the `partial` method of the `_Curryable`
    class provided here.

    >>> add_partial = partial(add3, 5, 6)
    >>> add_partial(7)
    18
    """
    _callable = func

    @_callable._partial_
    def wrapped_func(*args, **kwargs):
        bound_values = {}
        bound_values.update(bound_args)
        bound_values.update(kwargs)
        
        full_args = [*args]
        
        # convert keywords to positional args
        for k, v in bound_values.items():
            if k not in kwargs:
                full_args.insert(k, v)
                
        return _callable(*full_args)

    return wrapped_func


class _Curryable:
    def __init__(self, fn: Callable):
        self.fn = fn
        self.bound_args = {}
        self.bound_kwargs = {}

    def __call__(self, *args, **kwargs):
        self.bound_args.update({k: v for k, v in zip(self.fn.__code__.co_varnames[-len(args):], args)})
        self.bound_kwargs.update(kwargs)
        return self
    
    # this _partial_ decorator is also implemented as the partial method
    def _partial_(self, /, *bound_args, **bound_kwargs):
        new_self = type(self)(self.fn)
        new_self.bound_args.update(bound_args)
        new_self.bound_kwargs.update(bound_kwargs)
        return new_self
        
    
int_adder = _Curryable(int).fn


@_Curryable.add3
def add4(a, b, c, d):
    return a + b + c + d


@_Curryable
def square(x):
    return x**2


@square.partial
def cubic(x):
    return x**3

@cubic._partial_
def quartic(x):
    return x**4


if __name__ == "__main__":
    print(christmas_tree())
    print(list(filter_even(range(20))))
    print(list(map_factorial(range(20))))
    print(sieve_of_eratosthenes(20))


# ──────────────────────── TRAMPOLINE ────────────────────────────────────────

class Trampoline:

    def __init__(
        self,
        *,
        state=None,
        error=None,
        value=None,
