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

    def __get__(self, inst, cls):
        if inst is None:
            return self 
        result = self.func(inst)
        setattr(inst, self.attrname, result)
        return result


def Typed(**kwdargs):
    """Class decorator to create class with type-checked fields."""
    for name, expected_type in kwdargs.items():
        assert hasattr(expected_type, "__origin__"), (
            f"Expected a generic type as parameter for the field '{name}' "
            "of a typed class but found a non-generic type."
        )
        kwdargs[name] = expected_type[1]
    return lambda cls: class_decorator(cls, **kwdargs)


def class_decorator(cls, **kwargs):
    # Get slots of base classes. If there are none, the default value is an empty list.
    baseslots = [base.__slots__ or [] for base in cls.__bases__]

    # Iterate over all attributes of the decorated class, except builtins like `str` and `int`.
    for name, value in vars(cls).items():
        if (not isinstance(value, (staticmethod, classmethod))) and (not name.startswith("__")):
            if isinstance(value, (property, cached_property)):
                continue
            if isinstance(value, TypedDescriptor):
                continue
            if value not in (None, object()):
                cls_attrs[name] = value
                continue

        # Find out what kind of slot this attribute should be.
        setattr(cls, name, _make_slot_attribute(baseslots, name, value))

    # Add new slots from all base classes.
    for baseslot in itertools.chain(*baseslots):
        setattr(cls, baseslot, None)

    return cls


class _SlotAttribute:
    def __init__(self, name):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        try:
            return getattr(instance, "_" + self.name, None)
        except AttributeError:
            raise RuntimeError(
                f"The attribute '{self.name}' couldn't be accessed because it's missing."
            )

    def __set__(self, instance, value):
        setattr(instance, "_" + self.name, value)


def _make_slot_attribute(base_slots, name, value):
    """Create a slot attribute based on its type."""
    if value is None:
        return _Slot