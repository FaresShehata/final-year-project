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
        self.name: str = ""
        self.readonly = False
        self.writable = True
        self.fget = lambda *args, **kwargs: None
        self.fset = lambda *args, **kwargs: None
        self.deleter = lambda *args, **kwargs: None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    @property
    def fn(self) -> Callable[..., T]:
        """The function backing the property."""
        return self.fget or self.func

    def __get__(self, instance, cls=None):
        if instance is None:
            # The descriptor has been accessed from its class, i.e. `cls`
            return self.fn(cls)
        else:
            val = self.fn(instance)
            if not self.readonly:
                setattr(instance, self.name, val)
            return val

    def __set__(self, instance, value: T):
        if not self.writable:
            raise AttributeError("{0}.{1} is read-only".format(type(instance).__name__, self.name))
        setattr(instance, self.name, value)

    def setter(self, func):
        self.fset = func
        return self


def make_descriptor(name: str, validator: Callable[[Any], bool] | None = None) -> Descriptor:
    """
    Make a descriptor with default methods for get/set/deleter.
    """

    class Descriptor:
        @property
        def name(self) -> str:
            return "_" + name

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return getattr(obj, self.name, None)

        def __set__(self, obj, value):
            if validator is not None and not validator(value):
                raise TypeError(
                    "{0}.__set__: expected {1}, got {2}".format(
                        type(obj).__name__, validator.__name__, type(value).__name__
                    )
                )

            setattr(obj, self.name, value)

    return Descriptor()


# ── Metaclasses ──────────────────────────────────────────────────────────────

class MetaClass(type):

    def __new__(
        mcs,
        classname: str,
        superclasses: tuple[type],
        attributes: dict[str, Any],
    ):
        obj = super().__