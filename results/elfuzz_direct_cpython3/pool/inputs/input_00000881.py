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

add_2 = add(2)

print(add_2(5))


# ── Partial application using callables as arguments to other callables ───────

def add(x: int, y: int) -> int:
    return x + y

def apply(func: Callable[[int], int], val: int) -> int:
    return func(val)


apply(int, "4") == 4


# ── Trampoline implementation of the factorial function with explicit stack ──

def fact(n):
    state = {
        'acc': 1,
        'stack': [(n, lambda acc, n: (acc * n, n - 1))]
    }
    while True:
        try:
            acc = state['stack'][-1][0]
            n = state['stack'][-1][1]
            if n > 1:
                state['stack'][-1] = (acc * n, n - 1)
                continue
        except IndexError:
            break
        finally:
            state.pop('stack')
        yield acc
    raise ValueError(f'{n} is not allowed')


for i, v in enumerate(fact(6)):
    print(i, v)

try:
    next(fact(-1))
except ValueError as e:
    print(e)


# ── Trampoline implementation of the factorial function with implicit stack ──

class FactorialException(Exception):
    pass

def fact_tramp(n):
    acc = 1
    while n >= 1:
        try:
            acc *= n
            n -= 1
        except FactorialException:
            # Yielding `None` here would cause stopiteration exception
            # and we'd never get out of this loop.
            yield None
    return acc

for i, v in enumerate(fact_tramp(7)):
    print(i, v)
try:
    next(fact_tramp(-1))
except StopIteration as e:
    print(e.value)


# ── The power of lambda expressions in Python and functional programming ──────

lambda_add = lambda x, y: x + y
list(map(lambda_add, [1, 2, 3], [4, 5, 6]))
[7, 8, 9]


map(lambda s: s.upper(), ['hello', 'world'])


async def echo(msg):
    print(msg)
    await asyncio.sleep(1)
    return msg

async def main():
    async for stream in echo('Hello'):
        print(stream)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


def noop_func():
    ...


noop_lambda = lambda : ...
type(noop_lambda) == type(noop_func)


# ── Comprehension and generator expressions in Python ─────────────────────────

comprehension = [i ** 2 for i in range(5)]
generator = (i ** 2 for i in range(5))

print(comprehension)
next(generator)
list(generator)


# ── Generators and iterator protocol from scratch ─────────────────────────────

class StringIterator:

    def __init__(self, string):
        self.string = string
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == len(self.string):
            raise StopIteration
        char = self.string[self.index]
        self.index += 1
        return char

string_iterator = StringIterator('abcd')

print(next(string_iterator))



def iter(iterable):
    """Generates an iterator over iterable."""
    iterator = iter(iterable)
    while True:
        try:
            yield next(iterator)
               break