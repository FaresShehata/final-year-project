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

def fact(n):
    def step(acc, n):
        if n <= 1:
            return {'value': acc}
        else:
            return {'state': (acc * n, n - 1)}

    return trampoline(step, (1, n))

trampoline = lambda fn, args: \
    (lambda f, a: f(f, a))(
        lambda f, a: (
            lambda s: s['value']
            if ('done' in s) else
            trampoline(f, {**s, **{'state': f(**s['state'])}}))[fn](args),
        {'done': False, 'state': args}[None])[None]


for i, v in enumerate(fact(6)):
    print(i, v)

try:
    next(fact(-1))
except ValueError as e:
    print(e)



# ── Higher-order functions and decorators ─────────────────────────────────────

def repeat(times: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(8)
def say_hello():
    print('hello')

say_hello()


def memoize(func):
    cache = {}

    def inner(*args):
        key = str(args)
        if key not in cache:
            cache[key] = func(*args)
        return cache[key]

    return inner

@memoize
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

fib_cache = {}
memoized_fib = memoize(fib)

for i in range(11):
    print(i, fib_cache.get(i, i), fib_cache.get(i, i) == memoized_fib(i))



# ── Generators for producing Fibonacci sequence ───────────────────────────────

def fibonacci():
    previous, current = 0, 1
    while True:
        yield previous
        previous, current = current, previous + current

for i, v in zip(range(11), fibonacci()):
    print(i, v)


# ── Comprehensions and generators ───────────────────────────────────────────-

# Python list comprehension
lists_comprehension = [i for i in range(10)]
print(lists_comprehension)

# Python