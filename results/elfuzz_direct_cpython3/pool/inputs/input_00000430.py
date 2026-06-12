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


print(add3(1)(2)(3)) # => 6

# ── Partial application
add_5  = add3(5)
add_42 = add3(42)

print(add_5(7)) # => 12
print(add_42(9)) # => 51


# ── Trampoline example ───────────────────────────────────────────────────────

def fib_trampolined(n: int) -> Iterator[int]:
    yield from fib_trampolined(n - 1) if n > 1 else [0] + [1]
    while True:
        try:
            a, b = next(itertools.tee((yield from fib_trampolined)))
            yield a + b
        except StopIteration as e:
            break
    print("Done")


def fib_iterative(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    for i in range(n):
        yield a
        a, b = b, a+b


class FibTrampolineError(Exception):
    pass


def trampoline(fib_gen):
    gen = iter(fib_gen())
    res = next(gen)
    while True:
        try:
            step_fn = next(gen)
        except StopIteration as e:
            return e.value
        try:
            res = step_fn(res)
        except FibTrampolineError:
            continue
        except TypeError:
            raise FibTrampolineError()


fib_gen = fib_trampolined(8)
print(trampoline(fib_gen))


# ── Introducing and using functional programming tools ───────────────────────

nums = list(range(10))
squares = map(operator.pow, nums, repeat(2))
cubes  = map(operator.pow, nums, repeat(3))
sums   = zip(nums, squares, cubes)


for num, square, cube in sums:
    print(num, square, cube)



def filter_odd(numbers: Iterable[int]) -> Iterator[int]:
    for number in numbers:
        if number % 2 == 0:
            yield number


evens = list(filter_odd(nums))


def is_even(number: int) -> bool:
    return number % 2 == 0


even_nums = filter(is_even, nums)


# ── Higher order functions – reduce, map, filter, sort, etc.

def my_reduce(func: Callable[[Any, Any], Any], iterable: Iterable[Any],
              initial=None):
    it = iter(iterable)
    if initial is None:
        value = next(it)
    else:
        value = initial
    for element in it:
        value = func