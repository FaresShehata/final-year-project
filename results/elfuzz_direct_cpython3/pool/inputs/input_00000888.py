"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
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

    def __repr__(self) -> str:
        if not self._instances:
            return "<empty>"
        return (
            "<singleton "
            + ", ".join(repr(type(v)) for type(v) in self._instances.values())
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
    A dictionary mapping keys to dictionaries which map key/value pairs back.
    This was inspired by a similar structure used internally in `dict`.
    """

    def __getitem__(self, key: str) -> dict:
        d = super().__getitem__(key)
        if not d:
            d[key] = {}
        return d[key]


# ── Lambda calculus church encodings ──────────────────────────────────────────


class ChurchBooleans:
    """Church booleans."""
    
    TRUE  = lambda t: lambda f: t
    FALSE = lambda t: lambda f: f
    
    AND   = lambda p: lambda q: p(q)(p)
    OR    = lambda p: lambda q: p(p)(q)
    NOT   = lambda p: p(FALSE)(TRUE)

    def __bool__(self) -> bool:
        raise NotImplementedError()


# ── Currying & partial application ────────────────────────────────────────────


class AutoCurry:
    """
    A mixin class for auto-currying methods.
    
    Methods must be defined as staticmethods or classmethods when using this
    mixin. 
    """

    def __init_subclass__(subclass):
        for name, method in subclass.__dict__.items():
            if isinstance(method, (staticmethod, classmethod)):
                try:
                    # Try to get the underlying function object
                    method = getattrimport itertools
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
    """Accumulate and average a sequence of numbers."""

    total = init
    count = 0

    def accumulate(value: float) -> float:
        nonlocal total, count
        total = total + value
        count = count + 1
        return total / count

    return accumulate


# ── Partial application with variables as parameters ───────────────────────────

def take_n(func: Callable, n: int) -> Callable[[Iterable[A]], list[B]]:
    """Generate the first N results from a unary function over iterables."""
    return lambda iterable: list(itertools.islice(map(func, iterable), n))


def is_odd_count(items: Iterable[int]) -> bool:
    return sum(map(bool, filter(operator.not_, items))) % 2 != 0


# ── Higher-order functions & lambdas ───────────────────────────────────────────

def inc(lazy_func: Callable[[int], int]) -> Callable[[int], int]:
    """Increment by one."""
    return lazy_func(lazy_func)


def take_5(lazy_func: Callable[[int], int]) -> Callable[[int], int]:
    """Take five values."""
    return lazy_func(lazy_func(lazy_func))



# ── Trampolines ───────────────────────────────────────────────────────────────


class TrampolineError(Exception): pass

class Thunk:
    "Thunking wrapper around a computation."
    
    def __init__(self, thunk, *args, **kwargs):
        self.thunk = thunk
        self.args = args
