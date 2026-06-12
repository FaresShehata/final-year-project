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
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same CachedProperty to two different names "
                f"in the same scope ({self.attrname!r} and {name!r})."
            )

    def __get__(self, instance, owner):
        if instance is None:
            return self
        res = instance.__dict__[self.attrname] = self.func(instance)
        return res


def TypedType(expected_type, name=None):
    """Metaclass for enforcing a single argument type."""
    # Inherit docstrings from base class.
    namespace = dict(__doc__=expected_type.__doc__)
    if name is not None:
        namespace["name"] = name
    result_class = types.new_class(name or expected_type.__name__, (expected_type,), {}, lambda ns: ns.update(namespace))
    return result_class


# ─── CLASS EXAMPLES ───────────────────────────────────────────────────────────

class TypedMeta(type):
    """Metaclass that checks all arguments of the constructor."""

    @classmethod
    def __prepare__(metacls, cls, bases):
        return {"_attrs": []}

    def __new__(metacls, classname, bases, classdict):
        attrs = [attr for attr in classdict["_attrs"]
                 if not attr.startswith("_") and not callable(attr)]
        print(classname, attrs)
        members = [(key, val) for key, val in classdict.items() if key[0].islower()]
        for name, member in members:
            assert hasattr(member, "__annotations__")
            for attr_name, attr_type in member.__annotations__.items():
                if attr_name not in attrs:
                    continue
                other_attrs = set(attrs).difference({attr_name})
                if len(other_attrs) == 0:
                    break
                else:
                    raise TypeError(
                        "Expected one attribute per parameter; found multiple for %s." % name
                    )
                arg_names = tuple(getattr(member, "_args", ()))
                if any(arg_name == attr_name for arg_name in arg_names):
                    raise TypeError("Found duplicate attribute name for %s." % name)
                other_args = set(arg_names).difference({attr_name})
                if len(other_args) == 0:
                    break
                else:
                    raise TypeError(
                        "Expected one argument per parameter; found multiple for %s." % name