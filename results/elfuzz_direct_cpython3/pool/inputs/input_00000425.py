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

class Trampoline:

    def __init__(self, func: Callable, *args: Any):
        self.func = func
        self.args = args

    def __iter__(self) -> Iterator:
        while True:
            try:
                yield from self.func(self.args)
            except StopIteration as e:
                break


# ── Coroutines with send and throw ─────────────────────────────────────────────

async def coroutine(a: Any) -> float | None:
    print("coroutine started", id(coroutine), file=sys.stderr, flush=True)
    await asyncio.sleep(2)
    if a > 5:
        raise Exception("Too big!")
    else:
        return a-4


async def main():
    res = await coroutine(7)
    print(res)


# ── Unpacking tuples of varying length ────────────────────────────────────────

a = (1, 2, 3)
b = [4, 5, 6]

print(list(zip(a, b)))
print(list(zip_longest(a, b)))

for i in zip(range(len(a)), a, b):
    print(i)

for i in zip_longest(range(len(a)), a, b):
    print(i)

d = {"a": 1, "b": 2}
e = {"c": 3, "d": 4}

print({})
print({**{**d, **e}})
print(**{"**": d, "**": e})


# ── Packing dictionaries into tuples of varying length ─────────────────────────

a = ("a", 1)
b = ("b", 2)
c = ("c", 3)

print(tuple((i for _, i in (a, b, c))))
print()
print(tuple((i for _, i in ((a,), (b,), (c,)))))
print(tuple((i for _, i in list((a, b, c)))))

for i in zip(a, b, c):
    print(i)
for i in zip((a,), (b,), (c,)):
    print(i)
for i in zip(((a,),), ((b,),), ((c,),)):
    print(i)

for i in zip_longest(a, b, c):
    print(i)
for i in zip_longest((a,), (b,), (c,)):
    print(i)
for i in zip_longest(((a,),), ((b,),), ((c,),)):
    print(i)


# ── Structs, namedtuples, dataclasses, etc. ──────────────────────────────────

class Foo:
    def __init__(self, a: int, b: int) -> None:
           return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

