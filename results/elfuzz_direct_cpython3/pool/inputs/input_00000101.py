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
        result = x
        while m > 0:
            result = add(result, n)
            m = pred(m)
        return result
    return _mul


def inc(n: int) -> int:
    """Church increment."""
    return add(1, n)


def dec(n: int) -> int:
    """Church decrement."""
    return sub