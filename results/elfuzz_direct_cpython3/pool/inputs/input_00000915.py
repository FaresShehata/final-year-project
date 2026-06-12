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

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value} must be {self.expected_type}")
        if self.lo is not None and value < self.lo:
            raise ValueError(
                f"value out of range [{self.lo}, {self.hi}): {value}"
            )
        elif self.hi is not None and value > self.hi:
            raise ValueError(f"value out of range [{self.lo}, {self.hi}): {value}")

        setattr(obj, self.name, value)

    def __repr__(self):
        return repr(getattr(self, self.name))


class Typed(TypedDescriptor):
    """Class decorator to create a typed descripto which can optionally enforce a value range."""

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        self.name = self.name.replace("__", ".")

    def __set__(self, obj, value):
        super().__set__(obj, value)
        setattr(obj, self.name, value)



class Integer(TypedDescriptor): 
    """Integer descriptor.""" 

    def __set__(self, obj, value):
        super().__set__(obj, value)
        setattr(obj, self.name, value)


class Float(TypedDescriptor):
    """Float descriptor.""" 
 
    def __set__(self, obj, value):
         super().__set__(obj, value)
         setattr(obj, self.name, value)


class String(TypedDescriptor):
    """String descriptor."""

    def __set__(self, obj, value):
        super().__set__(obj, value)
        setattr(obj, self.name, value)


class IntegerRange(TypedDescriptor):
    """Integer range descriptor.

     A special case of the TypedDescriptor where the range is specified in __init__
     rather than __set__, such that values outside the range cannot be assigned.
    """
    return TypedDescriptor(expected_type, lo=lo, hi=hi)


@contextlib.contextmanager
def checked_range(lo: int | float, hi: int | float) -> Generator[None, None, None]:
    """Context manager that checks whether its contents were within a range."""
    try:
        yield
    except TypeError as e:
        raise TypeError(f"{e.args[0]} in {range(lo, hi)}")


def check_subclass(cls: type, expected_class: type) -> bool:
    """Return True iff cls is a subclass of expected_class."""
    return issubclass(cls, expected_class)

# ── Context managers ──────────────────────────────────────────────────────────


class ClosableMixin:
    """A mixin class for classes with resources that need closing."""

    _closed: bool = False

    @property
    def closed(self) -> bool:
        return self._closed

    def close_resource(self) -> None:
        pass

    def close(self) -> None:
        if self.closed:
            return
        # TODO: implement actual resource closure mechanism (for example,
        # using a context manager)
        print(f"{self} being closed.")
        self.close_resource()
        self._closed = True

    def __del__(self) -> None:
        self.close()


class OpenedFile(ClosableMixin):
    """A file open for reading and writing."""

    def __init__(
        self, filename: str, mode="r", encoding="utf-8"
    ) -> None:
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.fh = open(filename, mode=mode, encoding=encoding