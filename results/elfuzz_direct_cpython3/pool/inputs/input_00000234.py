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
AND   = lambda x: lambda y: x(y)(x)
OR    = lambda x: lambda y: x(x)(y)

# ─── Higher-order functions ─────────────────────────────────────────────────


def add(a: int) -> Callable[[int], int]:
    return lambda b: a + b


def double(a: A) -> A:
    return a * 2


# ─────────────────────────────────────────────────────────────────────────────


def is_even(n: int) -> bool:
    return n % 2 == 0


# ─── Comprehension / generator expressions ────────────────────────────────────


class xrange:

    def __init__(self, start=0, end=sys.maxsize):
        self.i = start - 1

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.i >= end:
            raise StopIteration
        self.i += 1
        return self.i


def infinite_xrange(start=0):
    while True:
        yield start
        start += 1


def natural_numbers() -> Generator[int, None, None]:
    for i in itertools.count(1):
        yield i


def evens() -> Generator[int, None, None]:
    i = 0
    while True:
        i += 2
        yield i


# ─── Infinite streams of values ───────────────────────────────────────────────


def stream(func: Callable[[], int]) -> Iterable[int]:
    """Generates values from function func."""
    while True:
        value = func()
        yield value


@functools.cache
def fib(n: int) -> int:
    """
    Calculates the nth Fibonacci number using only the first two numbers.
    """

    # Base case: F(0) = 0 and F(1) = 1
    if n <= 1:
        return n

    # Recursive case: F(n) = F(n-1) + F(n-2)
    else:
        return fib(n - 1) + fib(n - 2)


def fibonacci_stream():
    """
    Generates Fibonacci numbers.
    """
    # Start with the first two Fibonacci numbers, F(0) = 0 and F(1) = 1
    a, b = 0, 1

    #