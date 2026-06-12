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


# ── Higher-order functions ─────────────────────────────────────────────────────

def map(func: Callable[[Any], A], seq: Iterable[B]) -> Iterable[A]:
    for elt in seq:
        yield func(elt)


def filter(pred: Callable[[Any], bool], seq: Iterable[Any]) -> Iterable[Any]:
    for elt in seq:
        if pred(elt):
            yield elt


def reduce(func: Callable[[A, B], A], seq: Iterable[B], initial=A()) -> A:
    reduced = initial
    for elt in seq:
        reduced = func(reduced, elt)
    return reduced


def accumulate(
    func: Callable[[A, B], A],
    seed: A,
    iterable: Iterable[B],
    *,
    initializer=None
) -> A:
    accumulator = seed
    if initializer is not None:
        accumulator = initializer
    for elt in iterable:
        accumulator = func(accumulator, elt)
    return accumulator


def product(seq: Iterable[int]):
    return reduce(operator.mul, iter(seq))


def sum_of_squares(iterable: Iterable[int]):
    return accumulate(operator.add, 0, iterable, initializer=0 ** 2)


def cartesian_product(seq1: Iterable[T], seq2: Iterable[U]) -> Iterable[tuple[T, U]]:
    return ((a, b) for a in seq1 for b in seq2)


def permutations(seq: Iterable[T]) -> Iterable[tuple[T, ...]]:
    length = len(seq)
    indices = tuple(range(length))
    yield from (_permutation(indices) for _ in range(factorial(length)))
    raise StopIteration


def _permutation(indices: tuple[int, ...]) -> tuple[int, ...]:
    length = len(indices)
    pivot = indices[length - 1]
    while True:
        yield indices[:]
        for i in reversed(range(length - 1)):
            if indices[i] < pivot:
                break
        else:
            raise StopIteration
        indices[i], indices[pivot] = indices[pivot], indices[i]
        pivot -= 1
        indices[:] = indices[:pivot+1] + indices[pivot:length]


def factorial(num: int) -> int:
    acc = 1
    for i in range(2, num + 1):
        acc *= i
    return acc


def fibs(count: int) -> Iterator[int]:
    last = 1
