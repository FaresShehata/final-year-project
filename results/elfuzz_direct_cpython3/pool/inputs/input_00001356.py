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


def is_true(p: bool) -> bool:
    """Church truth value checker."""
    return p(True)(False)


def not_(p: bool) -> bool:
    """Church negation."""
    return p(lambda _: True)(_)


def or_(*ps: bool) -> bool:
    """Church disjunction."""
    def _or(ps):
        for p in ps:
            if p():
                return True
        return False
    return _or(ps)


def and_(*ps: bool) -> bool:
    """Church conjunction."""
    def _and(ps):
        for p in ps:
            if not p():
                return False
        return True
    return _and(ps)


def implies(a: bool, b: bool) -> bool:
    """Church implication."""
    return not_(a)() or b()


def iff(a: bool, b: bool) -> bool:
    """Church equivalence."""
    return a() == b()


def zero() -> int:
    """Zero function."""
    return 0


def succ(n: int | str) -> int:
    """Successor function."""
    n += 1
    return n


def pred(n: int) -> int:
    """Predessor function."""
    n -= 1
    return n


def add(m: int, n: int) -> int:
    """Church addition."""
    m = int(m)
    n = int(n)

    def _add(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = succ(result)
            m = pred(m)
        while n > 0:
            result = succ(result)
            n = pred(n)
        return result
    return _add(m)


def mul(m: int, n: int) -> int:
    """Church multiplication."""
    m = int(m)
    n = int(n)

    def _mul(x: int):
        nonlocal m
        nonlocal n
        result = zero()
        while m > 0:
            result = add(result, x)
            m = pred(m)
        return result
    return _mul(n)


def div(m: int, n: int) -> int:
    """Church division."""
    m = int(m)
    n = int(n)

    def _div(q: int):
        nonlocal m
        nonlocal n
        q = zero()
        while n <= m:
            q = succ(q)
            m = sub(m, n)
        return q
    return _div(q)


def rem(m: int, n: int) -> int:
    """Remainder of division by Church integers."""
    m = int(m)
    n = int(n)

    def _rem(r: int):
        nonlocal m
        nonlocal n
        r = m
        while n <= m:
            r = r - n
            m = pred(m)
        return r
    return _rem(r)



def curry(f: Callable[[Any], Any]) -> Callable[[Callable[[_T]], _T]]:
    """
    Curry an arbitrary unary function.

    >>> from math import sin
    >>> sin_curried = curry(sin)
    >>> sin_pi = sin_curried(pi)
    """

    def _curry(g: Callable[[_T], _R]) -> Callable[[_U], _R]:
        def _closure(*args, **kwargs):  # pylint: disable=unused-argument
            return g(*args, **kwargs)
        return _closure

    return _curry



# ── Partial application ────────────────────────────────────────────────────────

class PartiallyAppliedFunction(Callable):
    """
    A callable that remembers its arguments so far.
    
    It can be called again with more args to create another
    partially applied instance, which will remember the current
    set of arguments together with those passed to it.
    """

    def __init__(self, func: Callable[..., Any], *args, **kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> Any:
        new_args = (*self.args, *args)
        new_kwargs = {**self.kwargs, **kwargs}
        return self.func(*new_args, **new_kwargs)

    def __repr__(self) -> str:
        return f"<{self.func}({', '.join(map(repr, self.args))})>"

    def __eq__(self, other:            + ", ".join(repr(type(v)) for type(v) in self._instances.values())
            + ">"
        )

    def __str__(self) -> str:
        if not self._instances:
            return ""
        return (
            "<singleton "
            + ", ".join(str(type(v)) for type(v) in self._instances.values())
            + ">"
        )

    def __new__(cls, *args, **kwargs):
        """For Python 3.7+ use `if not cls._instances:` instead."""
        if not cls._instances:
            return super().__new__(cls)
        else:
            raise RuntimeError("singleton already instantiated!")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if isinstance(value, DefaultFactory):
                cls._instances[value] = cls


class IdentityDict(dict[str, dict]):
    """
