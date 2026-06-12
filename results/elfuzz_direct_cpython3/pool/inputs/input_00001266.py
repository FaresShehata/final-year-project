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

def curry(fn: Callable[A, B]) -> Callable[[A], Callable[[], B]]:
    def inner(arg: A) -> Callable[[], B]:
        return lambda: fn(arg)
    return inner


@functools.lru_cache(maxsize=None)
def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any) -> Any:
        if isinstance(args[-1], dict):         # cache on last arg being dict
            key = tuple(sorted(dict(args[-1]).items()))
            args = (*args[:-1], key)
        elif isinstance(args[-1], set):        # cache on last arg being set
            args = (*args[:-1], frozenset(args[-1]))
        try:
            return cache[args]
        except KeyError as err:
            cache[args] = ret = fn(*args)
            return ret
    return wrapper


# ── Trampoline syntax ─────────────────────────────────────────────────────────

class Trampoliner(Callable):

    def __init__(self, func: Callable[..., Any]):
        self.func = func
        super().__init__()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        while True:
            res = self.func(*args, **kwargs)
            if not isinstance(res, tuple) or len(res) != 2 \
                    or not isinstance(res[0], BaseException) \
                    or not callable(res[1]):
                break
            else:
                exc, handler = res
                kwargs.update(handler(exc))
        return res


@Trampoliner
def factorial(n: int) -> int:
    """Factorial with trampolining."""
    if n < 2:
        return n
    return (factorial(n - 1),
            {lambda e: ({'n': n}, {'result': n})})

@Trampoliner
def fibo(n: int) -> int:
    """Fibonacci numbers with trampolining."""
    if n == 1 or n == 2:
        return n
    return (fibo(n - 1),
            {lambda e: ({'n': n}, {'result': e['a'] + e['b']}),
             lambda e: ({'a': e['a'], 'b': e['b']},
                        {'a': e['b'], 'b': e['a'] + e['b']})
            }[e['i']])


# ── Comprehensions and generators ─────────────────────────────────────────────

def gen() -> Iterator[int]:
    yield from map(int, input().split())

print([*gen()])


def filter_gen(func: Callable[[int], bool]) -> Iterator[int]:
    for i in gen():
        if func(i):
            yield i

print(list(filter_gen(lambda x: x % 5 == 0)))


def even_gen() -> Generator[int, None, None]:
    i = 0
    while True:
        yield i
        i += 2

for i in even_gen():
    print(i)