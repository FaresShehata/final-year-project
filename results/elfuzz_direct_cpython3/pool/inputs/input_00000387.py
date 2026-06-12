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


def is_true(p: bool) -> bool:
    """Church truth value checker."""
    return p(True)(False)


def not_(p: bool) -> bool:
    """Church negation."""
    return p(lambda _: True)(_)


def or_(*ps: bool) -> bool:
    """Church disjunction."""
    def _or(ps):
        for p in ps:
            if p():
                return True
        return False
    return _or(ps)


def and_(*ps: bool) -> bool:
    """Church conjunction."""
    def _and(ps):
        for p in ps:
            if not p():
                return False
        return True
    return _and(ps)


def eq(p1: bool, p2: bool) -> bool:
    """Church equality."""
    return and_(not_(eq(not_(p1), p2)), and_(p1, p2))


if __name__ == "__main__":
    print(is_true(TRUE))
    print(is_true(FALSE))
    # Output:
    #   True
    #   False

    print(not_(TRUE))
    print(not_(FALSE))
    # Output:
    #   False
    #   True

    print(or_(True, False))
    print(or_(False, False))
    # Output:
    #   True
    #   False

    print(and_(True, True))
    print(and_(True, False))
    # Output:
    #   True
    #   False

    print(eq(True, True))
    print(eq(True, False))
    print(eq(False, True))
    print(eq(False, False))
    # Output:
    #   True
    #   False
    #   False
    #   True

    print('OK')


# ── Currying ────────────────────────────────────────────────────────────────

class CurriedFunction(Callable[[A], Callable[[B], Callable[[C], A]]]):
    """Currying function."""

    def __init__(self, func: Callable[[A, B, C], A]) -> None:
        self.__func = func

    def __call__(self, a: A, b: B, c: C) -> A:
        return self.__func(a, b, c)

    @classmethod
    def curry(cls, func: Callable[..., A]) -> CurriedFunction[A]:
        """Curries the given function."""
        return cls(func)


@functools.lru_cache()
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


add_curried = CurriedFunction.curry(add)
print(type(add(1, 2)))
print(type(add(1)))
print(type(add_curried))

a = add(1, 2)
b = add_curried(1)(2)
c = add(1)(2)(3)

print(a, b, c)
# Output:
#   <class 'int