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


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        while isinstance(f, Thunk):
            f = f()
        return f(*args)

    return wrapper


# ── Higher-order functions ─────────────────────────────────────────────────────

reduce = functools.reduce
map     = map
filter  = filter
zip     = zip
reversed = reversed


def compose_left(*fns: Callable) -> Callable:
    """Compose from the left side."""
    def composed(*args, **kwargs):
        value = args[-1]
        for fn in reversed(fns):
            value = fn(value, **kwargs)
        return value
    return composed


def compose_right(*fns: Callable) -> Callable:
    """Composes all given functions from the right side."""
    def composed(*args, **kwargs):
        value = args[-1]
        for fn in fns:
            value = fn(value, **kwargs)
        return value
    return composed


def repeat(n: int = 42) -> Callable:
    def repeater():
        print(n)


def run(func: Callable):
    func()


def run_all(*funcs: Callable):
    for func in funcs:
        func()


def apply_all(*funcs: Callable) -> list[Any]:
    return [func() for func in funcs]


def chunker(iterable: Iterable[A], size: int = 5) -> Iterator[tuple[A]]:
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


def take_while(predicate: Callable[[Any], bool]) -> Callable[[Iterable[A]], list[A]]:
    """
    Return an iterable which yields elements until predicate returns False.

    >>> list(take_while(lambda x: x < 3)(range(10)))
    [0, 1, 2]
    """

    def take_while_iter(iterable: Iterable[A]) -> Iterator[A]:
        for item in iterable:
            if not predicate(item):
                break
            yield item

    return take_while_iter


def drop_while(predicate: Callable[[Any], bool]) -> Callable[[Iterable[A]], list[A]]:
    """
    Return an iterable which drops elements until predicate returns False.

    >>> list(drop_while(lambda x: x > 3)(range(10)))
    [0, 1, 2, 3]
    """

    def drop_while_iter(iterable: Iterable[A]) -> Iterator[A]:
        skip_until_false = take_whileYou can also use descriptor protocol directly if you need to do some kind of validation.
'''

class NameDescriptor:
    def __set_name__(self, owner_class: type, attr_name: str):
        self.attr_name = "_" + attr_name

    def __get__(self, obj: PersonWithSetter, cls: type[PersonWithSetter]) -> str:
        return getattr(obj, self.attr_name)

    def __set__(self, obj: PersonWithSetter, value: str) -> None:
        setattr(obj, self.attr_name, value.upper())


class PersonWithSetter:
    name = NameDescriptor()

    def __init__(self, name: str):
        self.name = name


'''
