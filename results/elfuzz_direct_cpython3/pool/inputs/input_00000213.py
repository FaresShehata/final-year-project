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

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"
    
    @classmethod
    def get_subclasses(cls) -> list[type]:
        """Return all registered subclasses."""
        return [*cls._registry.values()]


def create_registry_cls(base: type | None = None) -> type:
    """Create a new subclassable metaclass with a custom _registry attribute.

    Args:
        base (type): Base class to inherit from. Defaults to ABCMeta.
    """
    return type(f"Registry{base.__name__}", (meta,) for meta in [abc.ABCMeta, base])


# ─── Abstract Classes ────────────────────────────────────────────────────────

class TitledEntity(metaclass=RegistryMeta):

    ...

class NamedEntity(TitledEntity):

    ...

class VisitableNamedEntity(NamedEntity):

    ...

class Visitable(TitledEntity):
    ...

class Store:
    pass
    
class Product(VisitableNamedEntity, Store):

    ...

class Service(VisitableNamedEntity, Store):

    ...

class Employee(VisitableNamedEntity):

    __slots__ = ["_id"]

    def __init__(self):
        self.id = id(self)

    # Not using the `@property` decorator because it's a method!
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value


# ── Concrete Subclasses ──────────────────────────────────────────────────────

class A(TitledEntity):
    pass


class B(A):
    pass



# ── Metaclasses ───────────────────────────────────────────────────────────────

class MyMeta(type):

    def __new__(metacls, name, bases, namespace):
        self = super().__new__(metacls, name, bases, namespace)
        print(f"New instance created: {name}({namespace})")
        return self



# ── Metaclasses - Subclassing built-in classes ───────────────────────────────

class MyList(list, metaclass=MyMeta):
    pass

mylist = MyList([1,2,3])

for i in mylist:
    print(i)



# ── Metaclasses - Subclassing user-defined classes ────────────────────────────

class MyDict(dict, metaclass=MyMeta):
    pass

mydict = MyDict({"a": 1})

print(mydict["a"])



# ──