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


# ── Partial function application & trampoline ------------------------------------------------------

def do_foo(a, b=2):
    print(a, b)


class Foo(object):

    def __init__(self, a, b=2):
        self.a = a
        self.b = b

    def foo(self):
        print(self.a, self.b)


do_foo_partial = functools.partial(do_foo, b=42)

foo_obj = Foo(7, 8)
foo_obj.foo()

foo_callable = foo_obj.foo.__func__
foo_callable()

do_foo_partial()
foo_callable()


def trampoline(func: Callable[..., object]) -> Callable[..., object]:
    """ Trampoline pattern implementation """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            res = func(*args, **kwargs)
            if isinstance(res, tuple):
                args, kwargs = res
            else:
                break
        return res
    return wrapper



@trampoline
def add(x: A, y: A) -> A:
    return x + y

assert add(5, 3) == 8


def coroutine_function(coro_func: Callable[[object], Generator[Any]]) -> Callable[[object], Generator[A]]:
    """ Make a generator that "coroutine" """

    @functools.wraps(coro_func)
    def wrapper(*args, **kwds):
        gen = coro_func(*args, **kwds)
        next(gen)
        return gen
    return wrapper


@coroutine_function
def counter(start_at=0):
    count = start_at
    try:
        while True:
            count += yield count
    except GeneratorExit:
        print('Generator Exiting')


counter_gen = counter()
next(counter_gen)
print(next(counter_gen)) # prints 0
print(next(counter_gen)) # prints 1

for i in [1, 2, 3]:
    counter_gen.send(i)

try:
    counter_gen.throw(ValueError())
except ValueError as e:
    pass


# ── Closures -------------------------------------------------------------------------------

def closure_example():
    outer_var = 'Hello'

    def inner_func():
        print(outer_var)

    return inner_func

closure_func = closure_example()
closure_func()


def counter_factory(starting_value=0):
    value = starting_value

    def incrementer():
