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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(
                f"Got {val!r}, which exceeds the range ({self.hi}) "
            )

        setattr(obj, self.name, val)


def typed(name: str) -> type:
    """
    Returns a new descriptor class with a single attribute named after self.

    The attribute is set by setting an instance of this descriptor on the target
    object. This can be done using the dot notation, or through calling it as a
    function (and passing the instance as first argument).

    >>> from pprint import pprint
    >>>
    >>> class Foo(object):
    ...     bar = typed('bar')
    ...
    >>>
    >>> pprint(Foo.bar)
    <some random object>

    If one wants to enforce specific values, they need to define the attributes
    `lo` and `hi`, e.g.

    >>> class Bar(object):
    ...     baz = typed('baz', lo=3, hi=7)
    ...
    >>>
    >>> pprint(Bar.baz)
    <some random object>
    """

    self = TypedDescriptor()
    self.name = ""
    return self


class TypedGenericMeta(type):
    def __new__(mcls, name, bases, namespace):

        attrs = {
            attr: TypedDescriptor() for attr in namespace.keys()
            if not attr.startswith("_")
        }
        return super().__new__(mcls, name, bases, namespace.update(attrs))


class TypedGeneric(metaclass=TypedGenericMeta):
    ...


# ── Context manager ───────────────────────────────────────────────────────────

@contextlib.contextmanager
def timer():
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(end - start)


# ── Generators ────────────────────────────────────────────────────────────────

def fibs(limit: int) -> Generator[int]:
    current, next_ = 0, 1
    while limit > 0:
        yield current
        current,import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 200


def prime(n) -> bool:
    i = 2
    while i < n:
        if n % i == 0:
            return False
        i += 1
    return True


class IntegerConstraint(_Constrained):
    pass


class PositiveInteger(IntegerConstraint):
    def __call__(self, x: int) -> bool:
        return positive(x)


class ShortStrConstraint(_Constrained):
    pass


class ShorterThanNCharsConstraint(ShortStrConstraint):
    def __init__(self, n: int):
        super().__init__()
        self.n = n

    def __call__(self, x: str) -> bool:
        return self.n >= len(x)


class PrimeNumberConstraint(ShorterThanNCharsConstraint):
    def __init__(self, n: int):
        super().__init__(n)
        self.n = n

    def __call__(self, x: int) -> bool:
        return prime(x)


# ── Typed generics ────────────────────────────────────────────────────────────

class Countable(Generic[T]):
    def __init__(self, count: int) -> None:
        self.count = count


class CounterList(Countable[list[int]]):
    ...


class CounterInt(Countable[int]):
    ...


class CounterFloat(Countable[float]):
    ...


CounterType = Annotated[type, ("Counter"), IntegerConstraint]
CounterABC = Annotated[CounterType, ("ABC")]


# ── Typing extras ─────────────────────────────────────────────────────────────

class MyDict(TypedDict):
    foo: int
