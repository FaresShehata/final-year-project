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
    def curried(*args):
        if len(args) >= fn.__code__.co_argcount:
            return fn(*args)
        else:
            return lambda *rest: curried(*(args + rest))

    return curried


def partial_application(func: Callable[[Any], A]) -> Callable[[Any], B]:
    @functools.wraps(func)
    def wrapper(arg2: B | None = None):
        # If arg2 is not None, it means the call was partially applied.
        if arg2 is not None:
            return func(arg2)
        # Otherwise, return a function that takes another argument and applies both arguments to func.
        else:
            return functools.partial(wrapper, arg2=arg2)

    return wrapper


@curry
def add(x: int, y: int) -> int:
    return x + y


add_5 = add(5)


# ── Partial application with functools partial ───────────────────────────────

def add_partial(x: int) -> Callable[[int], int]:
    """
    Create a new callable object that will call the original function with the current value of x as the first argument.

    Args:
        x: The initial value of x

    Returns:
        A new callable object that can be called with one argument and returns their sum.
    """

    def add(y: int) -> int:
        return x + y

    return add


add_5_p = add_partial(5)


# ── Trampoline / Tail-call optimisation ───────────────────────────────────────

class TCOError(Exception): pass

def trampoline(function: Callable[..., A]):
    """
    Decorator which wraps a generator-based recursive algorithm into trampoline.
    """

    @functools.wraps(function)
    def wrapped_function(*args, **kwargs):
        gen = function(*args, **kwargs)

        while True:
            try:
                ret_val = next(gen)
            except StopIteration as e:
                break

            if isinstance(ret_val, tuple):
                gen = ret_val[0]
                args = ret_val[1]
            else:
                gen = (ret_val,)

    return wrapped_function


@trampoline
def factorial(n: int) -> int:
    if n == 0:
        raise TCOError()

    yield (factorial(n-1), n - 1)
    return n


