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

    def __set_name__(self, owner: type, name: str) -> None:
        self.attrname = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None) -> object:
        if obj is None:
            return self
        try:
            return getattr(obj, self.attrname)
        except AttributeError:
            val = self.func(obj)
            setattr(obj, self.attrname, val)
            return val


@contextlib.contextmanager
def add_method(cls, attrname, method):
    """
    Context manager for adding attributes to a class dynamically.
    """

    old_attr = getattr(cls, attrname, None)
    if old_attr is None or not hasattr(old_attr, "__call__"):
        cls.add_to_class(attrname, method)
    else:
        print(f'WARNING: attempted to overwrite "{attrname}" in class {cls.__name__}')
    yield
    delattr(cls, attrname)
    if old_attr is None or not hasattr(old_attr, "__call__"):
        cls.remove_from_class(attrname)
    else:
        print(f'WARNING: failed to delete "{attrname}" from class {cls.__name__}')


# ─── CLASSES ─────────────────────────────────────────────────────────────────



class MyMeta(type):

    def __new__(meta, name, bases, namespace):
        new_namespace = {}
        for key, value in namespace.items():
            if isinstance(value, Descriptor):
                value.attrname = f"_{name.lower()}__{key}"
            new_namespace[key] = value
        return super().__new__(meta, name, bases, new_namespace)

    def __prepare__(meta, name, bases):
        return {"c": C}


class A(metaclass=MyMeta):

    """A simple example of using a metaclass."""

    b: B
    c: C

    def __init__(self, x):
        self.x = x


class Base(metaclass=MyMeta):

    """Trying out some inheritance with metaclass."""
    ...


class B(Base):

    def __init__(self, y):
        self.y = y
    pass


class C:

    def __init__(self, z):
        self.z = z




# ─── CLASSES ─────────────────────────────────────────────────────────────────



class Integer(TypedDescriptor):
    expected_type = int


class Float(TypedDescriptor):
    expected_type = float        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
