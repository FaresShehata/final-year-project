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
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # If the method is called with an instance, this will be None because
        # we have set `obj=None` in the constructor.
        cache = obj._cache
        if self.attrname:
            cache = cache.setdefault(self.attrname, {})
        result = cache.get(self)
        if result is None:
            result = cache[self] = self.func(obj)
        return result


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.cnt += 1
        print(wrapper.cnt, ":", end=" ")
        return func(*args, **kwargs)

    wrapper.cnt = 0
    return wrapper


@count_calls
def factorial(n: int) -> int:
    """Calculate n! (factorial of n)."""

    if n < 0 or not isinstance(n, int):
        raise ValueError("n must be a non-negative integer.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(5))
print(factorial.cnt)

# ── Protocol classes ─────────────────────────────────────────────────────────

class Comparable(metaclass=abc.ABCMeta):
    """ABC defining a protocol class used for equality comparison."""

    @classmethod
    @abc.abstractmethod
    def parse(cls, arg: str) -> Comparable:
        pass

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        pass

    def __gt__(self, other) -> bool:
        return other < self

    def __le__(self, other) -> bool:
        return not self > other

    def __ge__(self, other) -> bool:
        return not self < other


class IntComparable(int, Comparable):

    @classmethod
    def parse(cls, arg):
        try:
            return cls(int(arg))
        except ValueError:
            raise TypeError(f"Expected int, but got {arg}")

    def __eq__(self, other):
        return super().__eq__(other) if isinstance(other, IntComparable) else False

    def __lt__(self, other):
        return super().__lt__(other) if isinstance(other, IntComparable) else True

    def __repr__(self):
        return f"<IntComparable({super().__repr__()})>"


class StringComparable(str, Comparable):

    @classmethod
    def parse(cls, arg):
        try:
            return cls(arg.strip())
        except ValueError:
            raise TypeError(f"Expected string, but got {arg}")

    def __eq__(self, other):
        return super().__eq__(other) if isinstance(other, StringComparable) else False

    def __lt__(self, other):
        return super().__lt__(other) if isinstance(other, StringComparable) else True

    def __repr__(self):
        return f"<StringComparable({super().__repr__()})>"


some_ints = [IntComparable.parse(s) for s in ["4", "6", "-3"]]

for x in sorted(some_ints):
    print(x, end=" ")

some_strings = [StringComparable.parse(s) for s in ["   ", "hello!", "\tthere\n"]]
for x in sorted(some_strings):
    print(x, end=" ")

# ----| Comparing objects using operators |----
#

some_objects = [
    Object(a=1, b=2),
    Object(a=-3, b=4),
    Object(a=9, b=-8),
]
for o in sorted(some_objects):
    print(o, end=" ")

# ----| A simple example |----
#
<|file_sep|>/04_oop.py
#!/usr/bin/env python3
"""A simple class-based implementation of a generator function."""

import collections
import dataclasses
import enum
import math
import random
import statistics
import typing as t


class Distribution(enum.Enum):
    NORMAL = 0
    UNIFORM = 1
# The following line of text will be sent as an attachment.

# ----| A simple example |----
#


e send("Hello world")¶
def send(msg): pass¶
# Reply with a message object will be sent to the recipient.
#
# The following line of text will be sent as an attachment.

# ----| A multipart message |----
#
