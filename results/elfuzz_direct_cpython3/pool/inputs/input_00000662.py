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


def pow(base: int, exponent: int) -> int:
    """Church power tower."""
    base = int(base)
    exponent = int(exponent)

    def _pow(x: int):
        nonlocal base
        nonlocal exponent
        result = base
        while exponent > 0:
            result = mul(result, x)
            exponent = pred(exponent)
        return result
    return _pow(base)


def div(dividend: int, divisor: int) -> int:
    """Church division."""
    dividend = int(dividend)
    divisor = int(divisor)

    def _div(x: int):
        nonlocal dividend
        nonlocal divisor
        result = zero()
        while dividend >= divisor:
            dividend = sub(dividend, divisor)
            result = succ(result)
        return result
    return _div(dividend)


def mod(dividend: int, divisor: int) -> int:
    """Church modulus."""
    dividend = int(dividend)
    divisor = int(divisor)

    def _mod(x: int):
        nonlocal dividend
        nonlocal divisor
        remainder = zero()
        while dividend >= divisor:
            dividend = sub(dividend, divisor)
            remainder = succ(remainder)
        return remainder
    return _mod(dividend)


def leq(m: int, n: int) -> bool:
    """Church less-than-or-equal-to."""
    return m() <= n()


def geq(m: int, n: int) -> bool:
    """Church greater-than-or-equal-to."""
    return m() >= n()


def lt(m: int, n: int) -> bool:
    """Church less-than."""
    return m() < n()


def gt(m: int, n: int) -> bool:
    """Church greater-than."""
    return m() > n()


# ─────────────────────────────────────────────────────── Coroutines ───────────

class Async            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, "__%s__" % self.func.__name__)
        except AttributeError:
            val = self.func(obj)
            setattr(obj, "__%s__" % self.func.__name__, val)
            return val


class DefaultFactory(abc.ABC):

    def __call__(self, *args, **kwargs) -> Any:
        """Create a default instance of this factory's class."""
        cls = type(self)
        return cls.default(*args, **kwargs)


class Singleton(DefaultFactory):

    _instances: dict[type, type] = {}

    def __new__(cls, *args, **kwargs) -> Singleton:
        if cls in cls._instances.values():
            return cls._instances[cls]
        inst = super().__new__(cls, *args, **kwargs)
        cls._instances[cls] = inst
        return inst


class WeakSingleton(Singleton):
    """A singleton whose instances are kept track of by a weak reference.

    A weak singleton can outlive its original owner. For example:

      >>> class Foo:
      ...     x = WeakSingleton()

      >>> foo = Foo()
      >>> del foo
      >>> print(Foo.x)
      <weakref at 0x...; dead>
    """

    def __reduce__(self):
        return (super().__reduce__, (type(self),))


class SingletonDefault(DefaultFactory):
    """A default factory that returns an existing singleton instance."""

    _instances: dict[Any, Any] = {}
    _types: dict[Any, set[type]] = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        SingletonDefault._types.setdefault(cls, set())
        SingletonDefault._types[cls].add(type(cls))

    def __new__(cls, *args, **kwargs) -> SingletonDefault:
        if len(args) != 1 or kwargs:
            raise TypeError("__init__ takes exactly one positional argument")
        key = args[0]

        if key is None:
            for typ in SingletonDefault._types.get(cls, ()):
                if cls in typ._instances:
                    return typ._instances[cls]
            inst = super().__new__(cls)
            cls._instances[key] = inst
            return inst

        if key not in cls._instances:
            for typ in SingletonDefault._types.get(cls    """Trampoline: a data structure that represents an operation on a Maybe monad.
       The Maybe monad can be used to represent side-effects or errors without
       changing the core algorithm."""

    __slots__ = ("value", "tail")

