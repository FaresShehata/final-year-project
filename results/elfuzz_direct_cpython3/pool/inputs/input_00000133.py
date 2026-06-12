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
def add(a: A, b: B) -> C:
    return a + b



# ── Partial application & currying with lambdas ───────────────────────────────

add_2 = add(2)

add_2_lambda = lambda b: add(b, 2)


# ── Trampoline- and tail recursion using decorators ───────────────────────────

def trampoline(func):
    """Decorate a generator-based coroutine to use the trampoline pattern."""

    @wraps(func)
    def wrapper(*args, **kwargs):

        # The trampoline is just a stack of yielded values.
        # We can traverse it using the `yield from` syntax.
        result = func(*args, **kwargs)
        while True:
            try:
                yield next(result)
            except StopIteration as stop:
                break

    return wrapper

@trampoline
def countdown(count: int) -> Iterator[int]:
    if count > 0:
        yield from countdown(count - 1)
        yield count
    else:
        yield None


# ── Comprehensions, generators & iterators ───────────────────────────────────-

def first(iterable: Iterable[A]) -> A | None:
    iterator = iter(iterable[::-1])
    try:
        return next(iterator)
    except StopIteration:
        return None


def get_last(iterable: Iterable[A]) -> A | None:
    iterator = iter(iterable[::-1])
    last_val = next(iterator)
    for val in iterator:
        last_val = val
    return last_val


def flatten(iterables: Iterable[Iterable[A]]) -> Iterator[A]:
    for iterable in iterables:
        for item in iterable:
            yield item


def map_(func: Callable[[A], B], items: Iterable[A]):
    return (func(item) for item in items)


def filter_(predicate: Callable[[A], bool], items: Iterable[A]):
    return (item for item in items if predicate(item))


def zip_(items_a: Iterable[A], items_b: Iterable[B]):
    return ((a, b) for a, b in zip(items_a, items_b))


def enumerate_(items: Iterable[A]):
    index = 0
    for item in items:
        yield index, item
        index += 1


def product(numbers: Iterable[int]) -> int:
    prod = 1
    for number in numbers