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


def neq(p1: bool, p2: bool) -> bool:
    """Church non-equality."""
    return not_(neq(eq_(p1), p2))


def lt(p1: bool, p2: bool) -> bool:
    """Less than comparison."""
    return not_(lt(lt_(p1), p2)) and and_(p1, not_(lt(p2, p1)))


def gt(p1: bool, p2: bool) -> bool:
    """Greater than comparison."""
    return not_(gt(gt_(p1), p2)) and and_(p2, not_(gt(p1, p2)))


churchify = lambda x: lambda f: x(f)
unchurchify = lambda x: x()


def zero() -> int:
    """Zero."""
    return False


def one() -> int:
    """One."""
    return TRUE


def succ(n: int) -> int:
    """Successor of a number."""
    return churchify(churchify(n))(churchify(one()))


zero_ = zero()
one_  = one()

print(zero_)
print(succ(0))
print(succ(1))

assert is_true(and_(zero_, zero_))
assert is_false(neq(zero_, one_))
assert is_false(or_(is_true(zero_), is_false(one_)))
assert is_true(and_(zero_, zero_))
assert is_true(or_(is_true(zero_), is_false(one_)))

# ────────────────────────────────────────────────────────────────

# ── Closures ─────────────────────────────────────────────────────

def closure(x):
    def inner():
        return x
    return inner


a_closer = closure(42)

assert a_closer() == 42

closure_list = [closure(i + 1) for i in range(5)]

for c in closure_list:
    assert c() == c

closures_are_closures = [lambda x: x + 1](0)

assert closures_are_closures == 1

# ────────────────────────────────────────────────────────────────

# ── Higher-order functions ─────────────────────────────────────────

addition = lambda n: lambda m: n + m


assert addition(5)(6) == 11

def add_all(numbers: list[int]) -> int:
    acc = 0
    for n in numbers:
        acc += n
    return acc



# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()