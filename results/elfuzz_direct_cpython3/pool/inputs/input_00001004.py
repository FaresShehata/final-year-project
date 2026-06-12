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
    if arity == 0:
        return fn
    elif arity < 0:
        raise TypeError(f"Cannot curry {fn}.")
    else:
        return (lambda *args: (lambda arg: fn(*(args + (arg,))))(
            next(iter(args)))
                 if len(args) < arity
                 else fn(*(args)))

def uncurry(fn: Callable[[Any, ...], Any]) -> Callable[[Any, ...], Any]:
    """Uncurry a binary or unary function."""
    if fn.__code__.co_argcount == 1:
        return fn
    elif fn.__code__.co_argcount == 2:
        return fn
    else:
        return (lambda *args: fn(*args[:-1])(args[-1]))
    

# ── Partial application example: `partial` vs. `uncurry` vs. `functools.partial`
def adder(base: int = 0, increment: int = 1) -> int:
    return base + increment

adder_50 = partial(adder, increment=50)
adder_42 = partial(adder, base=42)
add_67 = UNCURRY(adder)(67)

print(add_67())
assert adder_50() == 50
assert adder_42() == 42


# ── Coroutines (`yield`, `send`) ─────────────────────────────────────────────

def countdown(n: int) -> Iterator:
    """Countdown generator."""
    while n >= 0:
        print(n)
        yield n
        n -= 1

for i in countdown(3):
    print(i)


async def countdown_async(n: int) -> Iterator:
    while n >= 0:
        await sleep(1)
        print(n)
        yield n
        n -= 1

async def main():
    async for i in countdown_async(3):
        print(i)

run(main())


async def countdown_yield(n: int) -> Iterator:
    """Generator-based countdown coroutine."""
    try:
        while True:
            await sleep(1)
            print(n)
            yield n
            n -= 1
    except StopAsyncIteration:
        pass

async def main():
    async with countdown_yield(3):

async def countdown_send(n: int) -> Iterator:
    """Coroutine that sends the current iteration."""
    while True:
        print(n)
        message = yield n
        if    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    ValuesView,
    overload,
)
from collections.abc import CallableMeta, CoroutineMeta, SequenceMeta
from dataclasses import dataclass, field, InitVar, fields, is_dataclass, replace
from datetime import date, datetime, timedelta
from numbers import Integral, Real
from functools import partial, reduce, wraps
from keyword import iskeyword
from math import ceil, factorial, floor, sqrt
from operator import indexOf
from pprint import PrettyPrinter
from reprlib import Repr
from shlex import split
from signal import Signals
from socket import gethostname
from sys import argv, version_info
from types import TracebackType
