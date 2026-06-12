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


counting_counter = counter()
double_counter = counter(100)


def memoized(fn):
    cache = {}

    def decorated_function(*args):
        if args not in cache:
            cache[args] = fn(args)
        return cache[args]

    return decorated_function


@memoized
def fibonacci(n):
    if n < 2:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


fibonacci(7)


def inc(x):
    return x + 1


def apply_incrementor(incrementor_fn):
    def wrapper(x):
        return incrementor_fn(x)

    return wrapper


increment_by_one = apply_incrementor(inc)
print(increment_by_one(7))

print(fibonacci(5))  # 5

for item in map(lambda x: x ** 2, [1, 2, 3]):
    print(item)

for item in filter(lambda x: x % 2 == 0, [1, 2, 3]):
    print(item)

for item in map(
    lambda x, y: x + y, [1, 3], [2, 4]
):  # note that the two lists must have equal length!
    print(item)

some_iterable = iter(range(9))
print(next(some_iterable))

# ── Generators ────────────────────────────────────────────────────────────────


def simple_generator_function():  # generator function
    yield 1
    yield 2
    yield 3


g = simple_generator_function()  # create a generator object
next(g)

# or use a generator expression
gen_expr = (x ** 2 for x in range(4))
print(gen_expr)
for item in gen_expr:
    print(item)

# ── Coroutines ────────────────────────────────────────────────────────────────


def coroutine_decorator(coroutine_fn):
    @functools.wraps(coroutine_fn)
    def wrapper(*args, **kwargs):
        g = coroutine_fn(*args, **kwargs)
        next(g)
        return g

    return wrapper


@coroutine_decorator
def average():
    total = 0
    count = 0

    while True:
        value = yield total / count
        print(value)
        total += value
        count += 1


ages_coroutine = average()

ages_coroutine.send(None)
ages_coroutine.send(1input_list = [
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