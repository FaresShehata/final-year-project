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


def is_true(p: bool) -> bool: return not p == FALSE

is_false  = is_true.__neg__
not_true  = is_false
not_false = is_true

true = TRUE(True)
false = FALSE(False)

assert all([
    true(1),
    false(2),
    is_true(true),
    is_false(false),
    is_false(not_true()),
    is_true(not_false())
])

assert all([
    True == is_true(TRUE(True)),
    False == is_true(FALSE(False))
])

zero   = lambda n: FALSE()
succ   = lambda n: lambda f: lambda x: n(f)(f(x))
pred   = lambda n: lambda z: n(lambda u: lambda v: v(u(z)))
add    = lambda m: lambda n: lambda s: lambda z: m(succ(n))(lambda y: pred(y)(z))
mult   = add(mult)
exp    = mult(exp)
div    = lambda m: lambda n: n(div(m))

assert all([
    zero(0),
    succ(zero)(0),
    pred(succ(pred(zero)))(0),

    add(one)(one)(two)(three)(four)(five)(six)(seven)(eight)(nine)(ten)(eleven)(twelve)(
        thirteen)(fourteen)(fifteen)(sixteen)(seventeen)(eighteen)(nineteen)(twenty)
])


assert all([
    one + one == two,
    three - one == two,
    four * two == six,
    five / two == two,

    exp(two)(three) == eight,
    div(three)(two) == one,
    div(eight)(two) == four
])

# ─── Higher-order functions and function composition ────────────────────────


def map(func: Callable[[Any], B], seq: list[A]) -> list[B]:
    """Returns a sequence with the elements of `seq` mapped with `func`.

    This function does not modify the original sequence.
    """
    result = []
    for item in seq:
        result.append(func(item))

    return result


def filter(predicate: Callable[[Any], bool], seq: list[Any]) -> list[Any]:
    """Filters out items of `seq` according to `predicate`, returning only those that satisfy it.

    This function does not modify the original sequence.
    """
    result = []
    for item in seq:
        if predicate(item):
            result.append(item)

    return result


