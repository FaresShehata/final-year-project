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


print(add3(1)(2)(3)) # => 6

# ── Partial application
add_5  = add3(5)
add_42 = add3(42)

print(add_5(7)) # => 12
print(add_42(9)) # => 51


# ── Trampoline example ───────────────────────────────────────────────────────

def fib_trampolined(n: int) -> Iterator[int]:
    yield from fib_trampolined(n - 1) if n > 1 else [0] + [1]
    while True:
        try:
            a, b = next(itertools.tee((yield from fib_trampolined)))
            yield a + b
        except StopIteration as e:
            break
    print("Done")


def fib_iterative(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    for i in range(n):
        yield a
        a, b = b, a+b


def fib_recursion(n: int) -> Generator[int, None, None]:
    if n == 1 or n == 2:
        yield 1
    else:
        a, b = 0, 1
        for _ in range(n-1):
            a, b = b, a+b
            yield a


fib_iter = iter(fib_iterative(sys.maxsize))
fib_rmc = iter(fib_recursion(sys.maxsize))
fib_tpm = iter(fib_trampolined(sys.maxsize))


for _ in range(10):
    print(next(fib_iter))
    print(next(fib_rmc))
    print(next(fib_tpm))


# ── Comprehensions and other iterators ───────────────────────────────────────-

a = [c for c in "Hello"]
b = {i**2 for i in range(10)}
c = (i+1 for i in range(10))
d = (j for j in range(8) if not j % 3)


class Fibs:
    def __init__(self):
        self.a = self.b = 1

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        return self.a

    def __iter__(self):
        return self

e = Fibs()


print(sum(i ** 2 for i in range(10)))
print({str(c) for c in "Hello"})
print(list(i + 1 for i in range(10)))
print([j for j in range(8) if not j % 3])

print(e)
print(next(e))
print(next(e))
print(next(e))
print(next(e))
print(next(e))
print(next(e))


# ── Generators and iterators ------------------------------------------------------------------------

def gen_func():
    yield 1
    yield 2
    yield 3


g = gen_func()
print(g.send(None)) # => 1
print(g.send(False)) # => 2
print(g.throw(ValueError('gen'))) # => 3
print(g.close()) # => None


def gen_func2():
    def helper(x):
        y = 2*x
        z = 3*y
        w = yield z
        v = 4*w
        u = yield v+z+w
        print(u)
        return z*u

    r = 10
    while True