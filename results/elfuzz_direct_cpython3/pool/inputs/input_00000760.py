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
class ContextManager:
    def __init__(self, value: bool = False) -> None:
        self.value = value
    
    @classmethod
    def wrap(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ctx_mgr = cls()

            try:
                yield ctx_mgr
                func(*args, **kwargs)
            finally:
                ctx_mgr.value = True
        
        return wrapper

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __bool__(self):
        return not self.value


class MyContextManager(ContextManager):
    def __init__(self, value: bool = False) -> None:
        super().__init__(value)

    def __str__(self):
        return "MyContextManager"


class MyContextManger2(ContextManager):
    def __init__(self, value: bool = False) -> None:
        super().__init__(value=value)

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



# ── Generators ────────────────────────────────────────────────────────────────

def generator_one():
    i = 0
    while i <= 5:
        yield i
        i += 1

def generator_two():
    i = 0
    while i <= 5:
        yield i
        i += 1
    else:
        print(f"Done generating numbers from 0 to 5")


def lazy_range(stop: int) -> Generator[int]:
    start = 0
    while start < stop:
        yield start
        start += 1

def lazy_range_two(stop: int) -> Generator[int]:
    start = 0
    while start < stop:
        yield start
        start += 1
    else:
        print(f"Done generating numbers from 0 to 5")


def lazy_fibonacci_sequence(n: int) -> Generator[tuple[int, int], None, None]:
    prev_num = 0
    curr_num = 1

    for _ in range(n):
        yield prev_num, curr_num
        prev_num, curr_num = curr_num, prev_num + curr_num

    print(f"Done generating n fibonacci sequence ({n}).")


class LazyFibonacciSequence:
    def __init__(self, n: int) -> None:
        self.n = n
        self.prev_num = 0
        self.curr_num = 1
    
    def __iter__(self):
        for _ in range(self.n):
            yield self.prev_num, self.curr_num
            self.prev_num, self.curr_num = self.curr_num, self.prev_num + self.curr_num

        print(f"Done generating n fibonacci sequence ({n}).")


def fib_generator(n: int) -> Generator[tuple[int, int], None, None]:
    a, b = 0, 1
    for _ in range(n):
        yield a, b
    def create_instance(self) -> Any:
        return type("", (), {})(*self.init_args, **self.init_kwargs)


