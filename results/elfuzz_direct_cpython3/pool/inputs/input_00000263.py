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
        if self.attrname is None:
            self.attrname = "_" + name
        elif not hasattr(owner, self.attrname):
            raise AttributeError(
                "Cannot set the attribute %s on class %s because another descriptor with the same name already exists." % (name, owner)
            )

    def __get__(self, instance, cls=object):
        if instance is None:
            return self
        if self.attrname is None:
            raise AttributeError(
                "%r should be accessed via %s.%s" % (
                    self,
                    cls.__name__,
                    self.attrname,
                ),
            )
        try:
            cache = instance.__dict__
        except AttributeError:
            # Instance doesn't support deserializing its dict. This may happen
            # when loading an object from pickled data.
            return self.func(instance)
        val = cache.get(self.attrname)
        if val is None:
            val = self.func(instance)
            cache[self.attrname] = val
        return val


class TypedAttr:
    """A typed attribute.

    >>> t = TypedAttr(int)(23)
    >>> t.value   # doctest:+ELLIPSIS
    23
    >>> t.value = 42
    >>> t.value
    42
    """

    def __init__(
        self, default: T = None, _is_required=False, desc: str = "", **kwargs
    ):
        self.default = default
        self._is_required = _is_required or kwargs.pop("_required", False)
        self.desc = desc
        self.kwargs = kwargs
        self.name = ""
        self.type_ = kwargs.pop("type_", None)

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = "_" + name
        if self._is_required and not hasattr(owner, self.name):
            raise AttributeError()

    def _raise_not_set_error(self, attrname, msg="Error accessing"):
        raise AttributeError("%s '%s' attribute; please check it was initialized" %
                             (msg.capitalize(), attrname))

    def __get__(self: TypedAttr[T], inst, owner=None) -> T:
        if inst is None:
            return self
        try:
            return getattr(inst, self.name)
        except AttributeError:
            if self.default is not None:
                setattr(inst, self.name, self.default)
