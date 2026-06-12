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
ISZERO = lambda n: IF(IF(n(())(lambda _: TRUE))(lambda _: FALSE))
SUCC  = lambda n: lambda s: lambda z: s(n(s)(z))
PRED  = lambda n: IF(ISZERO(n))(lambda _: FALSE)(lambda _: PRED(SUCC(n)))
ADD   = lambda m: lambda n: lambda s: lambda z: SUCC(m(n(s))(z))
MUL   = lambda n: lambda k: lambda s: lambda z: ADD(k)(n(s)(z))

# ── Closures and higher-order functions ───────────────────────────────────────


def make_adder(x):
    def adder(y):
        return x + y

    return adder


add_15 = make_adder(15)

print(add_15(-7))


def counter(start_at=0):
    count = start_at

    def incrementBy(step=1):
        nonlocal count
        count += step
        return count

    return incrementBy


c1 = counter()
c2 = counter(100)

print(c1())
print(c1())
print(c1())

print(c2())
print(c2())


def build_filter(predicate):
    def filter_list(input_list):
        return [element for element in input_list if predicate(element)]

    return filter_list


def is_odd(number):
    return number % 2 == 1


is_even = lambda number: not is_odd(number)


odd_filter = build_filter(is_odd)
even_filter = build_filter(is_even)

input_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

filtered_odds = odd_filter(input_list)
filtered_evens = even_filter(input_list)

print(filtered_odds)
print(filtered_evens)

# ── Comprehensions ────────────────────────────────────────────────────────────


def list_comprehension():
    # long way to write the same code:
    print([x ** 2 for x in range(4)])

    # short version using comprehension syntax
    print({x ** 2 for x in range(4)})
    print({x * 2 - 3 for x in range(4)})
    print({y ** 2 for y in range(10) if y > 5})
    print((i ** j for i in range(8) for