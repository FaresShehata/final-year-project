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
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val

MISSING = object()


# ── Metaclasses ──────────────────────────────────────────────────────────────


def classproperty(func):
    """Class method decorator.

    Similar to Python's `@classmethod` but for properties.
    """

    if not isinstance(func, (staticmethod, classmethod)):
        func = staticmethod(func)

    attrname = "__%s" % func.__name__

    @functools.wraps(func)
    def wrapper(cls):
        return getattr(cls, attrname)

    wrapper.__isabstractmethod__ = False
    wrapper.__func__ = func
    wrapper.__doc__ = func.__doc__

    setattr(cls, attrname, wrapper)

    return wrapper


class ABCMeta(abc.ABCMeta):
    """Metaclass that implements the abstract-method protocol.

    This can be used as a mixin or directly using the `with_metaclass`
    function. It uses `__abstractmethods__`, which is read-only in Python 2,
    so we use `__metaclass_abstract__`.
    """

    # Python 3 -- using __new__
    #
    # If you have the inheritance hierarchy correctly defined then this code
    # will work even when there are multiple levels of inheritance...

    # @classmethod
    # def __prepare__(metacls, name, bases):
    #     return super().__prepare__(name, bases)

    # @classmethod
    # def __new__(metacls, cls_name, bases, attrs):
    #     if "__abstractmethods__" in attrs:
    #         raise NotImplementedError("__abstractmethods__")
    #     abstract_methods = set(attrs.pop('__abstractmethods__', ()))
    #     for base in reversed(bases):
    #         abstract_methods |= set(base.__abstractmethods__)
    #     attrs['__abstractmethods__'] = frozenset(abstract_methods)
    #     return super().__new__(metacls, cls_name, bases, attrs)

    # Python 2 -- using __subclasscheck__ and __instancecheck__
    #
    # If you don't have the correct inheritance hierarchy, i.e. some classes
    # do not derive from other classes, then you should use this version.

    @classmethod
    def __add_abstract_method(mcs, cls, meth):
        if meth.__name__ in cls.__abstractmethods__:
            raise TypeError("%r already an abstract method" % meth.__name__)

        cls.__abstractmethods__ += (meth.__name__,)
        mro