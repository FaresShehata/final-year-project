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
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    return increment, reset


def make_adder(addend: int):
    state = addend

    def add(endorser: int) -> int:
        return endorser + state

    return add


def make_ddd():
    ddd = list(range(10))

    def get(i: int) -> int:
        return ddd[i]

    return get


def make_fib_iterator(max_n: int = 20):
    i, j = 0, 1

    while i <= max_n:
        yield i
        i, j = j, i + j


# ── Generators and iterators ──────────────────────────────────────────────────

def fibs(max_n=20):
    i, j = 0, 1

    while i <= max_n:
        yield i
        i, j = j, i + j


def is_palindrome(seq: Iterable[Any]) -> bool:
    """Iterative palindrome test from itertools."""
    it = iter(seq)
    try:
        front = next(it)
        back = next(it)
    except StopIteration:
        return True
    else:
        while front == back:
            try:
                front = next(it)
            except StopIteration:
                return True
            try:
                back = seq[(-1 - seq.index(front))]
            except ValueError:
                return False
        return False


def fibonacci(max_n=20):
    """Generator-based Fibonacci sequence.

    >>> tuple(islice(fibonacci(), 5))
    (0, 1, 1, 2, 3)
    """
    a, b = 1, 1
    while a < max_n:
        yield a
        a, b = b, a + b


# ── Comprehensions ───────────────────────────────────────────────────────────-

def comprehension_demo():
    """Demo of Python's list, dict, set, generator, and map comprehensions."""

    print("\nList comprehension:")
    xs = [i+1 for i in range(4)]
    ys = [(i, j) for i in range(3) for j in range(2)]

    print(xs, ys)

    print("\nDictionary comprehension:")
    square_map = {i: i*i for i in range(4)}

    print(square_map)

    print("\nSet comprehension:")
    odd_set = {i for i    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

