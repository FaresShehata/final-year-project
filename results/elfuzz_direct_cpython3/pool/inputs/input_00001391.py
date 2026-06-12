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
    

# ── Partial application and currying using functools.partial ──────────────────

add5 = functools.partial(add3, 5)


# ── Trampoline implementation with generator ──────────────────────────────────

def trampoline(fn: Callable): # pragma: no cover
    """Lifts a tail-recursive function into a trampolined closure,
       such that the original function can be called recursively without stack overflow."""

    @functools.wraps(fn)
    def wrapped(*args):
        while True:
            result = next(wrapped.generator, None)
            if result is not None:
                args = result[0]
            else:
                break
        return result[-1]
    
    @wrapped.autorun()
    def autorun(self, fn_):
        try:
            return self.generator.send(fn_(self.args))
        except StopIteration as e:
            return e.value
    
    wrapped.generator = iter(fn(*args))
    return wrapped


class ToplevelGenerator(Iterator[tuple]):
    pass


def autorun(self, fn):
    try:
        return self.generator.send(fn(self.args))
    except StopIteration as e:
        return e.value


def run(generator, args):
    while True:
        result = next(generator, None)
        if result is not None:
            args = result[0]
        else:
            break
    return result[-1]


@trampoline
def fibo(n):
    if n == 0 or n == 1:
        yield n, ()
    else:
        a, () = yield from fibo(n - 2)
        b, () = yield from fibo(n - 1)
        yield a + b, (a, b)

generator = ToplevelGenerator()


# ── Examples of functional programming ideas ──────────────────────────────────

# ── Higher order functions ────────────────────────────────────────────────────

# A function which takes another function as an argument.
def apply_twice(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return lambda x: func(func(x))


# A function which returns another function.
def compose(u: Callable[[Any], Any],
            v: Callable[[Any], Any]) -> Callable[[Any], Any]: 
    return lambda x: u(v(x))


# A function which applies itself once.
def identity(x):
    return x


# Higher