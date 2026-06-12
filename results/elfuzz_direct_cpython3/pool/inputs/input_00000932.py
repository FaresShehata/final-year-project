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
            mcs._registry[cls.__name__.lower()] = cls
        return cls

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return super().__prepare__(name, bases, **kwargs)

    @classmethod
    def get(mcs, __name__, default=...):
        try:
            return mcs._registry[__name__.lower()]
        except KeyError as err:
            if default is ...:
                raise LookupError(
                    __name__, "no such class in registry", mcs._registry.keys()
                ) from err
            else:
                return default


def inspect_abstract(cls) -> bool:
    for base in cls.mro():
        if hasattr(base, "__abstractmethods__"):
            return True
    return False


# ─── Base classes ─────────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


class BaseClass:
    """
    The simplest possible class. No attributes, no methods.
    """

    # Default value
    prop: int = 42


class MixinType(type, ABC):

    @property
    def attr(cls) -> str:
        return f"MixinType.{cls.__name__}.attr"


class AbstractClass(metaclass=MixinType):
    """
    An abstract class with an attribute inherited by its mixin.

    __init__ should never be called directly. Instead,
    create instances using the factory method `make_instance`.
    """

    @staticmethod
    def make_instance(name: str, *args, **kwargs) -> AbstractClass:
        __instance = globals().copy()
        instance = type(str(name), (AbstractClass,), {**__instance})(*args, **kwargs)
        return instance

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def __repr__(self):
        return self.__str__()


# ─── Concrete subclass ───────────────────────────────────────────────────────

class MyConcrete(AbstractClass):
    """A concrete implementation of `AbstractClass`."""

    attr: str = "MyConcrete.attr"
    x: str = "X"
    y: str = "Y"

    def __init__(self, name: str, *args, **kwargs):
        print("super()", super())
        print("self", self)
       