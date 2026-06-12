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
        owner.__dict__[self.name] = self

    def __get__(self, instance: T, owner: type) -> Any:
        return getattr(instance, self.name)

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}, got {type(value)}")
        setattr(instance, self.name, value)

    def __delete__(self, instance: T) -> None:
        delattr(instance, self.name)


class Typed(TypedDescriptor):

    def __set__(self, instance: T, value: Any) -> None:
        super().__set__(instance, self.validate(value))
        super().__delete__(instance)  # avoid descriptor leak

    def validate(self, value: Any) -> Any:
        return value


class Integer(Typed):
    expected_type = int


class Float(Typed):
    expected_type = float


class Range(Typed):
    expected_type = int

    def __init__(self, lo: Optional[int] = None, hi: Optional[int] = None, **kwargs):
        super().__init__(int, lo=lo, hi=hi)
        self.lo = lo
        self.hi = hi

    def __set__(self, instance: T, value: Any) -> None:
        values = (value, self.lo, self.hi)
        msg = (
            "Invalid range value",
            f"value should be between {self.lo} and {self.hi}",
            f"value is {value}",
        )
        for val in filter(None, values):
            if val != self.validate(val):
                raise ValueError(msg)
        super().__set__(instance, value)

    def validate(self, value: Any) -> Any:
        return value


# ── Metaclasses ───────────────────────────────────────────────────────────────

class Meta(type):
    def __new__(meta_cls, class_name, bases, class_dict):
        cls = super().__new__(meta_cls, class_name, bases, class_dict)
        cls._validate()
        return cls

    def __setattr__(cls, key, val):
        if hasattr(cls, "__metaclass__"):
            cls._validate()
        super().__setattr__(key, val)


class ABCMeta(type):
    def __new__(mcs, class_name, bases, class_dict):
        cls = super().__new__(mcs, class_name
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
