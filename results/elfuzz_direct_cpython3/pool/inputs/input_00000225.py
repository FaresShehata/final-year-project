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


def curried_add3(*args) -> Callable[..., int]:
    return add3(*args)


def partial_apply(fn: Callable, *args) -> Callable:
    return fn(*args)


add5 = partial_apply(add3, 5)
multiply_by_2_and_add_three = compose(curried_add3, add3, mul2)


# ── Monads and their instances ────────────────────────────────────────────────

def bind(fn: Callable, monad: object) -> object:
    """The `bind` operation of the monad instance `monad`."""
    raise NotImplementedError()


def maybe_map(monad: object, fn: Callable) -> object:
    """Map over `monad`, applying `fn` only to objects with a truthy value."""
    raise NotImplementedError()


def maybe_filter(monad: object, predicate: Callable) -> object:
    """Filter `monad` by applying `predicate` to all elements."""
    raise NotImplementedError()


def just(value: A) -> object:
    """Return an instance of `Just` containing `value`."""
    raise NotImplementedError()


def nothing() -> object:
    """Return an instance of `Nothing`.

    This is also called the `None` value of Haskell's `Maybe` monad.
    """
    raise NotImplementedError()


def do_block():
    pass


class Monad:

    def bind(self, fn: Callable) -> Monad:
        raise NotImplementedError()

    @classmethod
    def pure(cls, val: A) -> Monad[A]:
        raise NotImplementedError()


class Just(Monad):

    def __init__(self, value: A):
        self.value = value

    def bind(self, fn: Callable) -> Monad:
        return fn(self.value)

    @property
    def value(self) -> A:
        return self._value

    @value.setter
    def value(self, new_value: A) -> None:
        self._value = new_value

    @classmethod
    def pure(cls, val: A) -> Monad[A]:
        return Just(val)

    def __str__(self) -> str:
        return 'Just(%s)' % self.value

    def __repr__(self) -> str:
        return str(self)


class Nothing(Monad):

    def bind(self, fn: Callable) -> Monad:
        return self

    @classmethod
    def pure(cls, val: A) -> Monad[A]:
        return Nothing()

    def __str__(self) -> str:
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
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
