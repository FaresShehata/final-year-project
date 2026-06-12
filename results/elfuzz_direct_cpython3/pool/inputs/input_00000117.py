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


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

"""Metaclass for creating a class with methods to introspect its instance variables."""


def get_metaclass(name, bases, attrs):
    # Special case -- allow overriding base metaclass.
    basemeta = attrs.pop("__metaclass__", None) or bases[0]
    meta = basemeta(name, bases, attrs)
    # If it's a descriptor subclass, we'll need some extra setup.
    if issubclass(meta, DescriptorMeta):
        # The __new__ method will be called twice by the metaclass machinery,
        # once during initialization (before the __call__ on the base class),
        # and again when the actual class definition is created. We want to use
        # the second time around, so we have to check whether this is actually
        # being used as a class. This is done by checking for an existing
        # "__metaclass__" attribute in the class dict; if it exists, then we're
        # definitely using this class as a metaclass, otherwise, we'd just use
        # the base class' __new__.
        #
        # Note that this can't be checked in __init__, because __init__
        # is only called after the first __new__ has been called.
        if "__metaclass__" in meta.__dict__:
            meta = type(super(type, super(basemeta, meta)))
        else:
            meta = super(type, meta).mro()[len(basemeta.mro()):][0]
    return meta


class MetaClassBase(metaclass=get_metaclass):
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} at 0x{id(self):x}>"

    @property
    def instance_vars(self) -> tuple[Any]:
        return tuple(getattr(self, k) for k in dir(self) if not k.startswith("_"))

    @classmethod
    def from_instance(cls, inst: Any) -> "MetaClassBase":
        """Create a new class object based on the instance of the given class."""
        key = cls._instance_key(inst)
        klass = cls._instances[key]
        return cls(key, *klass.instance_vars)

    @staticmethod
    def _instance_key(inst: Any) -> tuple[type, ...]:
        return tuple(getattr(v, "__qualname__") for v in inst.__class__.__mro__)


class Singleton(MetaClassBase