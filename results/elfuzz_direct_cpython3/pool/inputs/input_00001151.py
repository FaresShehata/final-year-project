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
    def wrapped(*args):
        if len(args) < arity:
            return curry(wrapped)
        else:
            return fn(*args)

    return wrapped

@curry
def add(a: A, b: B) -> C:
    return a + b

add_one = add(1)
two_plus_three = add(add_one)(2)


# ── Partial application with functools.partial ───────────────────────────────-

def double(x: int) -> int:
    return x * 2

doubled_double_4 = functools.partial(double, 2)
print(doubled_double_4(4))    # 8


# ── Trampoline pattern ───────────────────────────────────────────────────────

class MyIterator(Iterator[int]):
    ...

it = iter(MyIterator())

next(it)   # OK
next(it)   # StopIteration exception

# or we can use the iterator protocol to implement it:

class MyTrampolineIterator:
    def __init__(self, func: Callable[[], Generator[Any, None, None]]) -> None:
        self.func = func

    def __iter__(self) -> MyTrampolineIterator:
        return self

    def __next__(self) -> int:
        for i in self.func():
            return i
        raise StopIteration

trampoline_it = MyTrampolineIterator(lambda: (yield from range(5)))

for i in trampoline_it:
    print(i)


# ── Partial application with Python's built-in partial ────────────────────────

def add1(x: int) -> int:
    return x + 1

add_two = functools.partial(operator.add, 2)

# and class-based implementations are also possible.

class AddTwo:
    def __call__(self, x: int) -> int:
        return x + 2

add_two = AddTwo()

# or using funtools

from functools import partial
add_two = partial(operator.add, 2)


# ── Partial application with lambdas ─────────────────────────────────────────

lambda_adder = lambda a: lambda b: a + b

adder_1 = lambda_adder(1)
adder_1(2)   # => 3

# or...

adder_2 = lambda (a, b): a + b
adder_2((1, 2))


# ── Partial application with currying ─────────────────────────────────────────

@curry
def add_curried(a: int, b: int) -> int:
    return a + b

add_1_and_2 = add_curried(1)(2)
add_7_and_9 = add_curried(7)(9)

#async def sleep(n: int | float) -> None:
    await asyncio.sleep(n)


async def coroutine_with_yield_from() -> int:
    yield from range(10)
    return sum(range(10))

coroutine_with_yield_from()


# ── Exceptions ───────────────────────────────────────────────────────────────

try:
    ...
except ZeroDivisionError as e:
    print(e.__str__())  # repr()
