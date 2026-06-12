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


class Typed(metaclass=TypedGenericMeta):
    pass


@typed
class MyInt(int):
    pass


MyInt(42)

with contextlib.suppress(TypeError):
    MyInt("foo")


# ── Metaclasses ───────────────────────────────────────────────────────────────

class A(type):
    @classmethod
    def m(cls):
        print(f"{cls=}")
        print(f"{type(cls)=}")

    def __call__(self, *args, **kwargs):
        print(self.m)
        print(*args)
        print(**kwargs)
        print(super())
        return super().__call__(*args, **kwargs)


class B(metaclass=A):
    ...


b = B()


# ── Context Managers ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def my_context():
    yield


with my_context():
    print("Inside context manager")


# ── Decorators ───────────────────────────────────────────────────────────────

def foo(bar="baz"):
    return "Foo " + bar


@functools.lru_cache(maxsize=5)
def fib(n):
    if n <= 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


fib(8)


# ── Generators ───────────────────────────────────────────────────────────────

def count(from_: int, to: int) -> Iterator[int]:
    while True:
        if from_ >= to:
            break
        yield from_
        from_ += 1


for x in count(from_=0, to=10):
    print(x)


def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1


print(next(infinite_sequence()))
print(next(infinite_sequence()))
print(next(infinite_sequence()))

# ── Scopes ───────────────────────────────────────────────────────────────────

x = "global"


def func():
    global x
    x = ""
    print(x)


func()
print(x)

x = "global"
y = "global"


def func():
    global x
    x = ""
    print(y)
    y = ""
    print(x)


func()
print(x)
print(y)

x = "global"


def func():
    global x
    x = ""
    print(x)
    del x


func()
