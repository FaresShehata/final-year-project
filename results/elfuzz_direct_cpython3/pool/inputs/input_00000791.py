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

    def _mul(y: int):
        nonlocal n
        result = 0
        while n > 0:
            result = add(result, y)
            n = pred(n)
        return result
    return _mul


def pow(b: int, e: int) -> int:
    """Church exponentiation."""
    b = int(b)
    e = int(e)

    def _pow(x: int):
        nonlocal b
        nonlocal e
        result = x
        while e > 0:
            result = mul(result, b)
            e = pred(e)
        return result
    return _pow


def fact(n: int) -> int:
    """Church factorial."""

    def _fact(x: int):
        nonlocal n
        result = 1
        while n > 0:
            result = mul(result, x)
            x = succ(x)
            n = pred(n)
        return result
    return _fact


if __name__ == "__main__":
    from doctest import testmod

    testmod()

    print(f"{'-' * 80}\n\n{is_true(FALSE)}\n{is_true(TRUE)}\n\n"
          f"{not_(TRUE)}\n{not_(FALSE)}\n\n{or_(True, True, True)}\n"
          f"{or_(True, False, True)}\n\n{and_(True, True, True)}\n"
          f"{and_(True, False, True)}\n\n{implies(False, True)}\n"
          f"{implies(True, True)}\n\n{iff(True, True)}\n{iff(True, False)}\n\n"
          f"{zero()} {succ(zero())} {pred(succ(pred(succ(zero()))))}"
          "\n\n{add(2, 4)} {sub(5, 4)} {add(add(2, 3), 4)}"
          "\n\n{mul(2, 4)} {div(6, 2)} {mul(sub(7, 2), 3)}"
          "\n\n{pow(2, 3)} {pow(5, 3)} {pow(2, sub(10, 3))}"
          "\n\n{fact(5)}\n")

# ──────── END OF FILE ─────────────────────────────────────────────────────────def test_code_object() -> None:

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__

    assert co.co_argcount == 3
    assert co.co_varnames == ("x", "y", "z")

    # TODO: add more tests


# ───