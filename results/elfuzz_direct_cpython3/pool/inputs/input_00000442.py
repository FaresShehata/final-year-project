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
    count = start
    def counter():
        nonlocal count
        count += step
        return count
    return counter


def make_adder(x: int) -> Callable[[int], int]:
    return lambda y: x + y


def outer_factory(param_1):
    def inner_factory(param_2):
        return param_1 + param_2
    return inner_factory


# ── Higher-order functions & map/filter/reduce/take/partition/map_by ─────────

def double(x: int | float) -> int | float:
    return 2 * x


def filter_even(nums: list[int]) -> list[int]:
    return [num for num in nums if num % 2 == 0]


def map_double(nums: list[int]) -> list[int]:
    return [double(num) for num in nums]


def reduce_plus(xs: list[int]) -> int:
    return sum([x for x in xs])


def take(count: int, iterable: Iterable[A]):
    return iter(itertools.islice(iterable, count))


def partition(pred: Callable[[Any], bool], iterable: Iterable[A]):
    return zip_longest(
        filter(pred, iterable),
        filterfalse(pred, iterable)
    )


def partition_all(count: int, iterable: Iterable[A]):
    it = iter(iterable)
    while True:
        chunk_it = islice(it, count)
        try:
            first = next(chunk_it)
        except StopIteration:
            return
        yield chain([first], chunk_it)


def filterfalse(predicate: Callable[[Any], bool],
                iterable: Iterable[Any]
               ) -> Iterator:
    # filterfalse(None, 'abcdef') --> 'bdf'
    "filter out all elements returning False to the predicate"
    if predicate is None:
        predicate = bool
    for element in iterable:
        if not predicate(element):
            yield element


# ── Comprehension and dictionary unpacking ────────────────────────────────────

chars_in_foo = {char: ord(char) for char in "foo"}
print(chars_in_foo)
{print(key) for key in chars_in_foo}


# ── Generators & iterators ───────────────────────────────────────────────────-

def gen_count(step: int = 1, limit: int | None = None):
    i = 0
    while limit is None or i < limit:
        yield