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
try:
    next(it)
except StopIteration as e:
    print(e)


# ── Comprehensions and generators ─────────────────────────────────────────────

nums_squared_lc = {i ** 2 for i in range(10)}
print(nums_squared_lc)

nums_squares_gc = (i**2 for i in range(10))                  # generator expression
for num_square in nums_squares_gc:
    print(num_square)

words_lc = [word.lower() for word in "Hello, world!".split()]
print(words_lc)

words_gc = ((word.lower() for word in "Hello, world!".split()))  # generator expression
for word in words_gc:
    print(word.upper())


# ── Coroutines --- send, throw, close ──────────────────────────────────────────

async def co():
    try:
        while True:
            msg = await input()
            print(msg)
    except KeyboardInterrupt:
        return "Goodbye"


async def main_coroutine():
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(co())

    try:
        task.send(None)             # Enter the coroutine.
        print(await task)           # Fetch the first value returned by the coroutine.
        await task                  # Wait until the coroutine terminates.
        await task.close()          # Close the coroutine.
    finally:
        await task.cancel()


# ── Higher order functions ---
#
# - map
# - filter
# - reduce
# - zip_longest
# - compose
# - flatmap
# - accumulate
# - partition
# - inspect
# - foldl/foldr
# - flap/flapr

def my_map(f: Callable[[Any], A], xs: Iterable[A]) -> list[A]:
    return [f(x) for x in xs]

def my_filter(pred: Callable[[Any], bool], xs: Iterable[Any]) -> list[Any]:
    return [x for x in xs if pred(x)]

def my_zip(a: Iterable[Tuple[Any]], b: Iterable[Tuple[Any]]) -> list[Tuple[Any]]:
    return [(x, y) for x, y in zip(a, b)]


# ── Closures ──────────────────────────────────────────────────────────────────

# Closure is an inner function that remembers values from the enclosing lexical scope even when the enclosing lexical scope has finished executing.


def counter(start_at=0):
    count = start_at

    def incr():
        nonlocal

@functools.total_ordering
class ConcreteClassA(AbstractClassA):
    x: int


class AbstractClassB(metaclass=RegistryMeta):
    y: int


@functools.total_ordering
class ConcreteClassB(AbstractClassB):
    y: int

    @property
    def z(self):
        return self.y * 2


if __name__ == "__main__":
    assert len(RegistryMeta._registry["AbstractClassB"]) == 1
    print(*sorted(RegistryMeta._registry.values()), sep="\n")
    # ConcreteClassB