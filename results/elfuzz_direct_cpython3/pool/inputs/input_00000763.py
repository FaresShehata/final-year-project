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


add5 = curry(add3)(5)                 # (a: int) => b: int => c: int => a+b+c
print(add5(7)(8)(9))


# ── Partial application with `partial` ─────────────────────────────────────────

from functools import partial

add5_10 = partial(add5, 10)
print(add5_10(7))


# ── Trampoline with yield ─────────────────────────────────────────────────────

def increment(x: int) -> int | tuple[int]:
    return x + 1


def inc_trpl(xs: Iterable) -> Iterator[None] | int:
    for x in xs:
        yield from increment(x)
        yield None


xs = [1, 2, 3, 4, 5]
for i in inc_trpl(xs): pass


# ── Itertools ─────────────────────────────────────────────────────────────────

items = ["a", "b", "c"]
for index, item in enumerate(items):
    print(index, item)

for _, item in enumerate(items):
    print(item)

for idx, item in enumerate(range(10)):
    print(idx, item)

print(next(itertools.islice([1, 2, 3], 2)))
print(list(itertools.takewhile(bool, [True, False, True])))
print(tuple(itertools.dropwhile(bool, [True, False, True])))

print(sum(itertools.count()))
print(reversed(range(10)))

it = iter(items)
print(type(it))
next(it)
next(it)
next(it)
try:
    next(it)
except StopIteration as e:
    print(e)

print(sys.getsizeof(items))


# ── Coroutines and send/throw/close ───────────────────────────────────────────

def coroutine() -> Generator[A, A, B]:
    while True:
        value = yield
        print(value)


def run_coroutine(coroutine_fn: Callable[..., Coroutine]) -> None:
    cr = coroutine_fn()
    try:
        next(cr)
        while True:
            value = yield
            cr.send(value)
    except StopIteration as e:
        print(e.value)


async def async_coroutine() -> Generator[B, C, D]:
    await asyncio.sleep(0)
    while True:
        value = yield
        print(value)


run_coroutine(asyncio.coroutine)

loop = asyncio.get_event_loop()
task = loop.create_task(async_coroutine())
loop.run_until_complete(task)


# ── Higher-order functions and closures ────────────────────────────────────────

def map(f: Callable[[A], B], xs: Iterable[A]) -> list[B]:
    result = []
    for x in xs:
        result.append(f(x))
    return result


map(int, [1, 2, 3])


def filter(pred: Callable[[Any], bool], xs: Iterable[Any]) -> list[Any]:
    result = []
    for x in xs:
        if pred(x):
            result.append(x)
    return result


filter(None, [True, False, True])

def reduce(
    op: Callable[[A, B], C],
    xs: Iterable[A],
    init: B = 0,
) -> C:
    """
    >>> reduce(operator.add, range(1, 4))
    6
    >>> reduce(operator.mul, range(1, 4), 2)
    24
    """
    acc = init
    for x in xs:
        acc = op(acc, x)
    return acc


reduce(operator.add, range(1, 4))


# ── Comprehensions ────────────────────────────────────────────────────────────

comps = [
    [i for i in range(10)]
    for j in range(10)]

comps = [[i ** 2 for i in range(10)] for j in range(10)]

with open("/home/nick/.ssh/id_rsa.pub") as file:
    pub_key = "".join(line.split())

pub_keys = [line.strip() for line in file]

files = [file.rstrip("\n") for file in file.readlines()]

result = [sum(i) for i in zip(*range(10))]