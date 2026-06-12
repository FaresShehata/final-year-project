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

print("\nChurch encoding:")
print(church_to_int(TRUE))       # => 1
print(church_to_int(IF(TRUE)(lambda x: print(x))(lambda y: print(y))))     # => True
for i in range(4):
    print(church_to_int(SUCC(i)))         # => 0, 1, 2, 3

print(int_to_church(1))           # => [0](x -> x+1)(0) = 1
print(int_to_church(2))           # => [1](x -> x+1)(0) = 2
print(int_to_church(3))           # => [2](x -> x+1)(0) = 3

print()

# ─── Closures ────────────────────────────────────────────────────────

# Closure is a function that can access variables from the outer scope even when
# it's not inside of the same scope.

# >>> def makeAdder(x):
# ...     def adder(y):
# ...         return x+y
# ...     return adder

# >>> plusOne = makeAdder(1)
# >>> plusTwo = makeAdder(2)

# >>> plusOne(5)             # => 6
# >>> plusTwo(5)             # => 7

# But actually we can do this using only one closure:

def make_adder(x: A) -> Callable[[int], A]:
    def adder(y: int) -> A:
        return x + y
    return adder


plus_one = make_adder(1)
plus_two = make_adder(2)


assert plus_one(5) == 6
assert plus_two(5) == 7

print("Closure:")
print(plus_one(5))      # => 6
print(plus_two(5))      # => 7

print()

# ── Higher-order functions ─────────────────────────────────────────────

map_ = iter(map)

sum_ = sum(range(5))

divisible_by_five = filter(lambda n: n % 5 == 0, range(10))

# >>> map(lambda s: s.upper(), ['spam', 'eggs', 'sausage']) \
...     == ['SPAM', 'EGGS', 'SAUSAGE']
... 
True

