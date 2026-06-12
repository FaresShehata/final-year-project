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
        if len(args) == arity:
            return fn(*args)
        else:
            return lambda *more_args: curried(*(args + more_args))

    return curried


def partial(fn: Callable, /, *args):
    """Partial apply the first N arguments to a function."""
    return lambda *more_args: fn(*args, *more_args)


@curry
def inc(x: A) -> B:
    return x + 1


@curry
def add(a: A, b: B) -> C:
    return a + b


inc_2 = inc(2)
add_2_4 = add(2, 4)


# ── Partial application with partial ──────────────────────────────────────────

def increment(n: int) -> int:
    return n + 1


def adder(n: int) -> int:
    return lambda m: n + m


print(add(5, 6)) # 11
print(adder(5)(6)) # 11

print(increment(5)) # 6
print(inc(5)) # 6

print(adder(5)(6)) # 11
print(add(5, 6)) # 11


# ── Trampoline implementation ────────────────────────────────────────────────

class Trampoline:
    def __init__(self, func: Callable[[Any], Trampoline]):
        self.func = func
    
    @classmethod
    def done(cls, val):
        return cls(lambda *_: val)

    @staticmethod
    def switch(funcs):
        while True:
            _, funcs = funcs[0](funcs[1:])
    
    def run(self, *args):
        return Trampoline.switch((func.run(*args) for func in self.func))


def fib(num: int):
    return Trampoline.done(-1) \
        .switch([
            lambda _: Trampoline.done(0),
            lambda _: Trampoline.done(1),
            lambda _: Trampoline(
                lambda state: (
                    Trampoline.done(state + 1).run() or 
                    Trampoline.fib(state - 1).run()
                )
            ),
        ])


for i in range(10):
    print(f"fib({i})={fib(i).done()}")