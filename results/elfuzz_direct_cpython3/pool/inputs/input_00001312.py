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


for i, v in enumerate(fact(6)):): print(i, v)
print([v for v in fact(6)])


def fact_tramp(n):
    def step(state):
        acc, count = state
        if count <= 1:
            return {'state': acc, 'done': True}
        return {'state': (acc * count, count-1)}
    initial_state = {'state': 1, 'done': False}
    while not initial_state['done']:
        gen = (step(initial_state)['state'])
        next(gen)
        try:
            state = gen.send(None)
            initial_state['state'], initial_state['done'] = state
        except StopIteration:
            pass
    return initial_state['state']


fact_tramp(7)
[gen.send(None) for _ in range(8)][::-1]

# ── The same algorithm can be implemented using an iterator ─────────────────-

def fact_iterative(n):
    acc = 1
    while n >= 2:
        acc *= n
        yield acc
        n -= 1

list(fact_iterative(8))