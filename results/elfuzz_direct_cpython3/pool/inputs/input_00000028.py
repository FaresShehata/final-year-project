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


class Dog(object):

    def speak(self) -> str:
        return "Woof!"

    def __repr__(self) -> str:
        return self.speak()


class Cat(object):

    def speak(self) -> str:
        return "Meow!"

    def __repr__(self) -> str:
        return self.speak()


def cat_dog(s: str) -> bool:
    cats = map(Cat, filter(lambda x: isinstance(x, Cat), s.split()))
    dogs = map(Dog, filter(lambda x: isinstance(x, Dog), s.split()))
    return all(map(still_speechless, zip(cats, dogs)))

def still_speechless(pair: tuple[Cat | Dog, Cat | Dog]) -> bool:
    cat_says, dog_says = pair
    return cat_says != dog_says


# ── Trampoline pattern ───────────────────────────────────────────────────────

class Trampoline(Iterator[A]):
    """Trampoline is a generator that yields another generator and returns the value."""

    def __init__(self, gen: Callable[[Any], Generator[Any, A, None]]):
        super().__init__()
        self._generator = gen(None)

    def _run_gen(self) -> Generator[Any, A, None]:
        try:
            while True:
                yield from self._generator()
        except StopIteration as e:
            return e.value

    def send(self, v: A) -> A:
        """Send an input to the generator without stopping it."""
        return next(self._run_gen(), v)

    def throw(self, exc: Exception) -> Generator[Any, A, None]:
        """Throw an exception into the generator."""
        return self._run_gen().throw(exc)

    def close(self) -> Generator[Any, A, None]:
        """Close the generator."""
        return self._run_gen().close()

    def __next__(self) -> A:
        """Return the next value of the generator or raise a StopIteration error."""
        return next(self._run_gen())

    def __iter__(self) -> Trampoline[A]:
        """Inherit iterator protocol."""
        return self


# ── Higher order functions ────────────────────────────────────────────────────

def constant(value: B) -> Callable[..., B]:
    """Returns a function that always returns the given value."""
    return lambda *