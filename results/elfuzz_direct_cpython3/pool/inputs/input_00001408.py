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
        return lambda *rest: curried(*(args + rest))

    return curried


@curry
def add(x: A | B, y: A | B) -> A | B:
    return x + y

add_2 = add(2)
print(add_2(4))  # 6
print(add_("a", "b"))  # 'ab'


# ── Trampoline-based recursion ───────────────────────────────────────────────

class Recurse:
    def __init__(self, value):
        self.value = value


class Done:
    pass


def factorial(n: int):
    def fact(n: int):
        if n == 1:
            return Done()
        else:
            return Recurse(n * fact(n - 1).value)
    return fact(n)


def main():
    print(church_to_int(int_to_church(5)))
    print(if_(True, TRUE, FALSE)("Hello")("World"))
    print(and_(true(), true())("And you?"))

    fib_iterative = lambda n: (
        b := lambda a, b: lambda c: c(a, b),
        i := lambda a: lambda b: lambda f: f(b)(lambda _: i(i)(i)),
        z := lambda a: lambda b: lambda f: b(a)(
            lambda c: f(c)(lambda d: d(d)(d))),
        i(ONE)(
            ZERO
        )(lambda f: lambda x: f(z)(z)(lambda g: lambda h: lambda _: g(h(g))(h))))
    fib_recursive = lambda n: (
        b := lambda a, b: lambda c: c(a, b),
        i := lambda a: lambda b: lambda f: f(b)(lambda _: i(i)(i)),
        z := lambda a: lambda b: lambda f: b(a)(
            lambda c: f(c)(lambda d: d(d)(d))),
        i(ONE)(
            ZERO
        )(lambda f: lambda x: f(z)(z)(lambda g: lambda h: lambda _: g(h(g))(h))))(
                lambda f: lambda n: (
                    ONE
                    if n == 0
                    else TWO
                    if n == 1
                    else f(n - 2).value + f(n - 1).value))
    print(next(fib_iterative(7)))
    print(next(fib_recursive(7)))

if __name__ == "__main__":
    main()