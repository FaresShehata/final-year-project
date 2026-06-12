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

    def __init__(self, func): # pylint: disable=super-init-not-called
        self.func = func
        self.name: str = ""
        self.weakref_cache: bool = False

    def __call__(self, instance):
        return self.__get__(instance, instance.__class__)

    def __get__(
        self,
        instance,
        owner
    ) -> Any:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            pass
        else:
            if self.weakref_cache:
                del instance.__dict__[self.name]

        result = value = self.func(instance)
        instance.__dict__[self.name] = value
        return result


# ─── Decorators ──────────────────────────────────────────────────────────────

def typed(*types):
    """Decorator for defining typed properties."""
    assert len(types) > 0

    def wrap(func):
        result = TypedList(func, *types)
        if len(types) == 1:
            # If there's only one type to check against, we can do the checking in the setter.
            # This is more efficient than doing it in the getter.
            @functools.wraps(func)
            def wrapper(self, value):
                if not isinstance(value, types[0]):
                    raise TypeError(
                        f'{func.__qualname__}: expected {types[0].__name__}, got {type(value).__name__}'
                    )
                func(self, value)
        else:
            # Otherwise, we need to do the checking in both the setter and getter.
            # We'll store the original implementation of the property so we can call it later.
            @property
            def wrapped_getter(self):
                if not hasattr(self, "__typed_" + func.__name__):
                    setattr(self, "__typed_" + func.__name__, func.__get__(self))
                return getattr(self, "__typed_" + func.__name__)

            @functools.wraps(func)
            def wrapper(self, value):
                if not isinstance(value, types):
                    raise TypeError(
                        f'{func.__qualname__}: expected {types.__name__}, got {type(value).__name__}'
                    )
                func(self, value)

            wrapper.getter(wrapped_getter)
        return result

    return wrap


class CallableMeta(type):
    """Metaclass to create callable classes."""

    def __new__(cls, clsname, bases, attrs):
        funcs = {}
        for