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


def implies(a: bool, b: bool) -> bool:
    """Church implication."""
    return not_(a)() or b()


def iff(a: bool, b: bool) -> bool:
    """Church equivalence."""
    return a() == b()


def zero() -> int:
    """Zero function."""
    return 0


def succ(n: int | str) -> int:
    """Successor function."""
    n += 1
    return n


def pred(n: int) -> int:
    """Predessor function."""
    n -= 1
    return n


def add(m: int, n: int) -> int:
    """Church addition."""
    m = int(m)
    n = int(n)

    def _add(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = succ(result)
            m = pred(m)
        while n > 0:
            result = succ(result)
            n = pred(n)
        return result
    return _add


def mul(n: int, m: int) -> int:
    """Church multiplication."""
    m = int(m)
    n = int(n)

    def _mul(x: int):
        nonlocal m
        nonlocal n
        result = 0
        for _ in range(pred(m)):
            result = add(result, n)
        return result
    return _mul


def inc(m: int | str) -> int:
    """Church natural number incrementer."""
    return succ(int(m))


def dec(m: int | str) -> int:
    """Church natural number decrementer."""
    return pred(int(m))


def num_to_bools(number: int) -> list[bool]:
    """Church's numeral to boolean sequence conversion.
       Uses Church's successor, predecessor and addition operations as the
       building blocks of the representation.

       >>> from random import randrange
       >>> all(num_to_bools(randrange(2**48)) == [False] * (randrange(2 ** 48)))
       True
    """
    assert isinstance(number, int), "Wrong type"
    assert number >= 0, "Negative numbers are not supported"
    res = []
    while number != 0:
        res.append(bool(number & 1))
        number >>= 1
    return res[::-1]


def bools_to_num(bools: list[bool]) -> int:
    """Boolean sequence to Church numeral converter.
       The algorithm uses Church's predecessor, successor and subtraction
       operations as the building blocks of the conversion process.

       >>> from random import randint
       >>> all(num_to_bools(random.randrange(2**48)) ==
       ...     bools_to_num(num_to_bools(random.randrange(2**48)))
       ... )
       True
    """
    assert len(bools) <= 64, "Too many bits!"
    assert any(bools), "Zero is not allowed"

    number, mask = 0, 1
    for bit in reversed(bools):
        if bit:
            number |= mask
        mask <<= 1
    return number


def church_number_to_int(church_number: Callable[[int], int]) -> int:
    """Converts a Church numeral to its integer representation.

    >>> church_number_to_int(succ(zero()))
    1
    >>> church_number_to_int(add(zero(), two()))
    2
    >>> church_number_to_int(mul(two(), three()))
    6
    """
    #