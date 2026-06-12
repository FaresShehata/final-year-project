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

def iter_map(it: Iterator[A], fn: Callable[[A], B]) -> Iterator[B]:
    while True:
        try:
            yield fn(next(it))
        except StopIteration:
            break


@pipe(map(int, ["1", "2", "3"]), sum, lambda s: f"sum({s})")
def test_pipe() -> str:
    pass


def test_compose_sum_ints():
    assert compose(add3, add3, add3)(1, 2, 3) == 9
    assert pipe(add3, add3, add3)(1, 2, 3) == 9


def test_compose_sum_ints_lambda():
    assert compose(
        lambda x: x + 1,
        lambda y: y + 2,
        lambda z: z + 3
    )(1, 2, 3) == 9


def test_compose_sum_ints_curried():
    assert add3.add3.add3(1)(2)(3) == 9


def test_compose_sum_ints_partial_application():
    assert add3(1, 2)(3) == 9


def test_pipe_sum_ints():
    assert pipe(add3, add3, add3)(1, 2, 3) == 9


def test_filter():
    assert list(filter(lambda x: x % 2 == 0, [1, 2, 3])) == [2]


def test_map():
    assert list(map(lambda x: x**2, [1, 2, 3])) == [1, 4, 9]


def test_iterate():
    assert list(iterate(1, lambda x: x*2)) == [1, 2, 4, 8, 16]


def test_reduce():
    assert reduce(lambda x, y: x+y, [1, 2, 3, 4], 0) == 10


def test_fold():
    assert fold(None, 1, add3)([1, 2, 3]) == 6
    assert fold("", "a", lambda x, y: x+y)("bcd") == "abcd"


def test_scanl():
    assert scanl(lambda x, y: x+y, 1)([1, 2, 3]) == [1, 3, 6]


def test_scanr():
    assert scanr(lambda x, y
    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total
    acc._init_value = init  # type: ignore[attr-defined]
    return acc

increment = make_accumulator()
reset = make_accumulator()


def test_make_accumulator():
    assert increment(1) == 1
    assert increment(5) == 6
    assert increment._init_value == 0.0
    assert reset() == 0.0
    assert increment(1) == 1


""" Closure and higher order functions """

def closure_example(arg: A) -> A:
    def inner(x: A = arg) -> A:
        return x  # type: ignore[return-value]
    return inner

closure_fn = closure_example(1)


# ── Higher order functions - map, filter, zip, etc.

def map_(fn: Callable[..., Any], iters: Iterable[Any] | None = None) -> Iterator[Any]:
    if not iters:
        return iter(fn())
    return map(fn, *iters)


def filter_(
    pred: Callable[[Any], bool],
    iters: Iterable[Any] | None = None
) -> Iterator[Any]:
    if not iters:
        return iter(pred())
    return filter(pred, *iters)


def zip_(*iterables: Iterable[Any]) -> Iterator[tuple[Any, ...]]:
    iterators = map(iter, iterables)
    while True:
        try:
            yield tuple(i.next() for i in iterators)
        except StopIteration:
            break


def take(n: int, xs: Iterable[A]) -> list[A]:
    return list(islice(xs, n))


def drop(n: int, xs: Iterable[A]) -> Iterator[A]:
    it = iter(xs)
    next(itertools.islice(it, n))  # Skip first n elements.
    return it


def isort(items: Iterable[A], reverse=False) -> list[A]:
    unsorted = items
    sorted_items = []
    while unsorted:
        minimum = min(unsorted, key=operator.itemgetter(reverse))
        sorted_items.append(minimum)
        unsorted.remove(minimum)
    return sorted_items


def partition(pred: Callable[[A], bool], xs: Iterable[A]):
    true_, false_ = [], []  # Initialize lists to empty values.
    for x in xs:
        if pred(x):  # If the predicate returns True...
            true_.append(x)  # Append the item to true_.
        else:
            false_.append(x)  # Otherwise append it to false_.
    return true_, false_


