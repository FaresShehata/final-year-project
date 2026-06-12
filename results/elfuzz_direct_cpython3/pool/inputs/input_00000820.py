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

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    @classmethod
    def __prepare__(cls, *args):
        # Ensure we inherit from the correct base class.
        cls = super().__prepare__(*args)
        cls.__bases__[1].__bases__ = (object,)
        return cls

    def __new__(mcs, name, bases, attrs, **kwargs):
        # Check for an explicit constructor.
        init = attrs.pop("__init_subclass__", None)
        if init is None:
            # No constructor provided. Use default behavior.
            return super().__new__(mcs, name, bases, attrs, **kwargs)
        else:
            # Define a new constructor that calls the superclass's one first.
            # This will ensure the registry is properly initialized.
            def __init__(cls, **kwargs):
                init(cls, **kwargs)
                cls._registry.append(cls)
            # Add the new constructor to our subclass dictionary.
            attrs["__init__"] = __init__

        # Initialize the registry list as a class variable.
        if "__slots__" in attrs:
            attrs["__slots__"].append("_registry")
        else:
            attrs["_registry"] = []

        # Create the class using the superclass's __new__ method.
        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        return cls

    def __call__(cls, *args, **kwargs):
        """Call the specified subclass constructor."""
        instance = super().__call__(*args, **kwargs)
        for subcls in cls._registry:
            if subcls is not instance:
                subcls.instances.append(instance)
        return instance


class AbstractClass(metaclass=RegistryMeta):
    """Abstract base class with a registry for its instances."""

    instances: list[Any]
    _registry: list[Type[AbstractClass]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.instances = []
        cls._registry = []


def make_a_class():
    return type("AClass", (), {})


def test_registry_metaclass():
    assert len(AbstractClass._registry) == 0
    AClass = make_a_class()
    assert len(AbstractClass._registry) == 1
    BClass = make_a_class()
    assert len(AbstractClass._registry) == 2
    CClass = make_a_class()
    assert len(AbstractClass._registry) == 3
    del