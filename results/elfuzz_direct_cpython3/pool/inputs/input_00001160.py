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
        self.cache = WeakKeyDictionary()


class WeakKeyDictionary(dict):
    """
    Dictionary that doesn't prevent the keys from being garbage-collected.

    >>> class A:
    ...     d = WeakKeyDictionary()
    ...
    >>> a1 = A()
    >>> a2 = A()
    >>> a1.d[a1]
    {}
    >>> a1.d[a2]
    {}

    The values are also weak-referenced:

    >>> a3 = A()
    >>> a1.d[a3]
    {}
    del a3
    >>> a1.d[a3]
    Traceback (most recent call last):
      ...
    KeyError: a3

    And can be iterated over:

    >>> for i in a1.d:
    ...     print(i)
    <object at 0x7f96bfaa48d0>
    <object at 0x7f96c0ea4e10>

    """

    def __missing__(self, key):
        self[key] = value = defaultdict(list)
        return value

    def __delitem__(self, key):
        super().__delitem__(key)
        for value in self.values():
            try:
                value.pop(key)
            except KeyError:
                continue


class AttrsMeta(type):

    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, T]) -> type[T]:
        # Add class attributes to all concrete subclasses of this class.
        cls.add_attrs(cls, attrs)
        new_class = super().__new__(cls, name, bases, attrs)
        # Add attrdict to non-concrete subclasses.
        for base in reversed(new_class.mro()):
            if "__attrs_attrs__" in base.__dict__:
                break
        else:
            continue
        new_class.__attrdict = AttrDict(attrs=base.__attrs_attrs__)
        return new_class

    @staticmethod
    def add_attrs(super_cls, attrs):
        """Add attrs to all subclasses of super_cls."""
        for subclass in super_cls.__subclasses__():
            if "__attrs_attrs__" in subclass.__dict__:
                continue
            subclass.__attrs_attrs__ = AttrsAttrs(attrs)


class AttrsAttrs(tuple):
    """Attributes for an Attrs class or subclass."""

    _instance = None

    def __new__(cls, attrs):
        self = super().__new__(cls, attrs.items())
        self._instance = cls
        return self

    def get(self, key, default=None):
        """Get an attribute by its name."""
        return next((v for k, v in self), default)


class AttrDict(MutableMapping):
    """A dictionary with typed attributes."""

    def __init__(self, attrs: AttrsAttrs):
        self.attrs = attrs
        self.data = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        if key in self.attrs:
            attr = self.attrs.get(key)
            if attr[1] is not None and not isinstance(value, attr[1]):
                raise TypeError(
                    "Attribute '%s' should have type %r"
                    % (key, attr[1].__name__)
                )
        self.data[key] = value

    def __iter__(self):
        yield from self.data.keys()

    def __len__(self):
        return len(self.data)

    def validate(self) -> bool:
        """Validate all attributes of the AttrDict instance."""
        for attr in self.attrs:
            try:
                self[attr[0]]
            except KeyError:
                pass
        return True

   