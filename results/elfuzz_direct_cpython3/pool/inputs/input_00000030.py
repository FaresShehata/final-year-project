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


def uncurry(fn: Callable[[Iterator], B]) -> Callable[[A, A], B]:
    """Uncurrying is the reverse of currying.

    It undoes the memoization that `uncurry` does and returns
    a regular callable.
    """
    return lambda x, y: fn(iter((x, y)))


def compose(f: Callable[..., B], g: Callable[..., A]) -> Callable[..., B]:
    """Composing two functions means applying them sequentially.

    Apply `f` to `g(a)` instead of `a`.
    """
    return lambda *args: f(g(*args))


@overload
def pipe(x: A) -> A:
    ...


@overload
def pipe(
    x: A,
    *functions: Callable[tuple[A], B],
) -> B:
    ....


def pipe(*args) -> Any:
    """Pipe all arguments through the given function(s).

    Similar to `reduce`, but from right-to-left instead of left-to-right.
    """
    return reduce(lambda f, g: compose(f, g), args[::-1])(*args[:-1])


def flip(f: Callable[[A, A], B]) -> Callable[[A, A], B]:
    """Flip the order of one argument in a binary function.

    i.e., `flip(f)(x, y) == f(y, x)`
    """
    return lambda x, y: f(y, x)


def once(func: Callable) -> Callable:
    """Only call `func` once and cache its result.

    Once you call `once()` twice with the same arg, it will be the second time
    you get back the same result as the first time.
    """
    called = False
    result = None

    @functools.wraps(func)
    def wrapper(*args):
        nonlocal called, result

        if not called:
            result = func(*args)
            called = True

        return result

    return wrapper


def trace(prefix=""):
    """Prints the arguments passed to a function before calling."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args):
            print(f"{prefix}({', '.join(map(str, args))})")
            return func(*args)

        return wrapper

    return decorator


@trace()
def add(a: int, b: int) -> int:
    return a + b


# ── Partial application ─
def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
