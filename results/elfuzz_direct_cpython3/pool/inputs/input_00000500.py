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
ADD   = lambda m: lambda n: m(SUCC)(n)
MUL   = lambda m: lambda n: lambda f: m(n(f))
SUB   = lambda m: lambda n: n(ZERO)(lambda s: SUCC(s(m)))
DIV   = lambda m: lambda n: SUB(ADD(m)(m))(MULT(m)(n))
MOD   = lambda m: lambda n: n(DIV(m)(n))(ZERO)
POWER = lambda m: lambda n: MUL(n)(m)
FACT  = lambda n: IF(GT(n)(ZERO))(
    LAMBDA() (
        MULT(n)(FACT(subtract(n)(ONE)))
    )
)(
    ONE
)

λ     = lambda x: lambda y: x(y)


def compose(*args):
    """Compose a list of unary functions."""
    if not args or len(args) == 1:
        return args[0]
    else:
        return lambda x: reduce(operator.__mul__, args[::-1])(x)


def curry(f: Callable[[A], B]) -> Callable[[A], Callable[[A], B]]:
    """
    Curry is a technique to convert a function with multiple arguments into
    a chain of unary functions.
    """

    return lambda x: lambda xs: [x] + xs


@functools.partial(curry, ZERO)
def multiply(a, acc):
    return acc + a


@curry
def add(x: A, ys: List[A]):
    return sum(ys) + x


@curry
def subtract(x: A, ys: List[A]):
    return sum(ys) - x


@curry
def divide(x: A, ys: List[A]):
    return sum(ys) / x


@curry
def modulo(x: A, ys: List[A]):
    return sum(ys) % x


@curry
def divide_by_zero_error(x: A, ys: List[A]):
    raise ZeroDivisionError()


@curry
def power(x: A, ys: List[A]):
    product = 1
    for y in ys:
        product *= x ** y
    return product


@curry
def zero(n: int, acc: int):
    return acc


@curry
def succ(n: int, acc: int):
    return acc + 1


@curry
def factorial(n: int, acc: int):
    return acc if n <= 1 else factorial(n - 1, succ(acc))


@curry
def factorials(xs: List[int], acc: List[int]):
    result = []
    for x in reversed(xs):
        result.append(FACT(x)(acc[-1]))
    return result



@curry
def factorials_tuple(xs: Tuple[int, ...], acc: Tuple[int, ...]):
    result = ()
    for x in reversed(xs):
        result += (FACT(x)(acc[-1]),)
    return result


# ── Trampoline implementation ───────────────────────────────────────-
def trampoline(func: Callable[..., Any]) -> Callable[..., Any]:
    """Return a version of func that can be called repeatedly without blowing the call stack."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                ret = func(*args, **kwargs)
            except RecursionError as err:
                print('!!! Recursion limit exceeded !!!')
                break
            if isinstance(ret, tuple) and len(ret) > 1:
                args, kwargs = ret
            elif isinstance(func, types.FunctionType):
                return wrapper(*ret)
            else:
                return ret
    return wrapper


# ── I/O helpers ───────────────────────────────────────────────────────

def read_int():
    return int(input())


read_str = input


# ── Church numeral computations ─────────────────────────────────────────

COMPOSE = compose(IF(GT(NONZERO)), FACT)

COMPOSE = compose(
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL    return COMPOSE(power(5))(fact)


COMPOSE = compose(
    FACTORIAL,
    POWER,
    MOD,
    DIV,
    POWER,
    SUBTRACT,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    POWER,
    DIV,
    ADD,
    FACTORIAL,
)

FACTORIAL = curry(factorial)

# ── Higher order functions, iterators and generators ─        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
