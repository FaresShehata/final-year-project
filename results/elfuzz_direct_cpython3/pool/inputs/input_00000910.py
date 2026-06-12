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
def add(a: A, b: B) -> A | B:
    return a + b

add_2 = add(2)

print(add_2(4))         # 6
print(add_2('a', 'b'))  # 'ab'
print(add_2(True, False))       # True
print(add_2((1, 2)))             # ((1, 2), (1, 2))


# ───── Partial application with functools.partial
def always_7(x):
    return 7

always_7 = functools.partial(always_7, arg=5)


# ── Trampolining ────────────────────────────────────────────────────────────

def trampoline(fn):
    while True:
        fn, args = fn()
        if not callable(fn):
            break;

    return fn(*args)

def countdown(n: int):
    print(str(n).zfill(len(str(sys.maxsize))))
    if n > 0:
        yield (countdown, n-1)

trampoline(countdown(1000))



# ── Lambdas and lambdification
def always_7(x):
    return 7

lambda_always_7 = lambda x: 7

for func in [always_7, lambda_always_7]:
    print(func(), end='\t')

print('\n\n')


# ── Higher-order functions and functions as first-class citizens
def sum_even_numbers(numbers: Iterable[int]) -> int:
    return sum(filter(lambda n: n % 2 == 0, numbers))

sum_even_numbers([1, 2, 3, 4, 5])


def apply_twice(fn: Callable[[int], int], number: int) -> int:
    return fn(fn(number))

apply_twice(lambda n: n * 2, 10)


def do_nothing():
    pass

do_nothing()