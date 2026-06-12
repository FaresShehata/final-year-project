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


# ── Partial application ─────────────────────────────────────────────────────

def partial(func: Callable[[A], B], /, **kwargs: A | None) -> Callable[..., B]:
    """
    Create a new function that is a partial application of `func` with the given
    keyword arguments.

    Parameters:
        func: The original function to be partially applied.
        kwargs: The keyword arguments that will be fixed in the new function.

    Returns:
        A new function that has some or all of its arguments bound.
    """

    def wrapped(*other_args: A) -> B:
        # Merge the fixed args with the other ones
        merged_args = {**kwargs, **dict(zip(kwargs.keys(), other_args))}

        # Call the original function with the merged args
        return func(**merged_args)

    return wrapped


add5 = partial(add3, c=5)


# ── Trampoline pattern ──────────────────────────────────────────────────────

def trampoline(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        while True:
            try:
                res = fn(*args, **kwargs)
            except StopIteration as e:
                return e.value
            else:
                args = ()
                kwargs.clear()
                if isinstance(res, tuple):
                    fn, args, kwargs = res
                elif isinstance(res, list):
                    fn, *res = res
                    args += res
                elif callable(res):
                    fn = res
            finally:
                pass
    return wrapped


# ── Comprehensions, generators, iterators, etc. ────────────────────────────

nums = [
    i for i in range(10_000)
]

even_numbers = (
    i for i in nums
    if not i % 2
)

square_nums = (
    num ** 2 for num in nums
)

pairs = (
    (num, num ** 2) for num in nums
)

odd_squares = ((i, j) for i in nums for j in nums if not i % 2 and not j % 2)

doubles = {
    i: i * 2 for i in nums
}


# ── Iterators and generators ────────────────────────────────────────────────

def double(n) -> int:
    return n * 2


iterable = map(double, filter(None, nums

async def asynchronous_for_loop(gen: AsyncIterator[T]) -> None:
    async for item in gen:
        print(item)


# ── Unpacking arguments and keyword arguments ────────────────────────────────

x = [1, 2, 3]
y = ["a", "b"]
z = {"c": 4}
x, *y, z = zip(x, y, z)


# ── Keyword-only arguments ──────────────────────────────────────────────────

def func(*, key="value") -> str:
    return key

func(key="new_value")


# ── Context managers ─────────────────────────────────────────────────