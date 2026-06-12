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


_MISSING = object()  # sentinel value for missing values in caches.


# ─── Clases abstractas ───────────────────────────────────────────────────────

class BaseClass(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def class_method(cls):
        ...


class AbstractBaseClass(BaseClass):
    ...

    @classmethod
    def class_method(cls):
        print(f"class method of {cls}")


# ─── Metaclasses ──────────────────────────────────────────────────────────────

class Meta(type):
    """Example of a metaclass with custom behaviour.

    This meta-class adds some extra functionality to the `int` class.
    """

    def __call__(self, *args, **kwargs):
        result = super().__call__(*args, **kwargs)
        result.__words = args
        print(result.__words)
        return result

@types.new_class(Meta, ["new"])
def new_class(name, bases, namespace: dict[str, Any], **kwds: Any):
    return super().__new__(cls, name, bases, namespace, **kwds)


# ─── Atributos de clases ──────────────────────────────────────────────────────

class ClassAttribute:
    """
    Class attribute example.
    """

    default_value: int = 3

    @classmethod
    def get_default_value(cls) -> int:
        return cls.default_value


# ─── Atributos de instancias ──────────────────────────────────────────────────

class InstanceAttribute:
    """
    Instance attribute example.
    """

    instance_var = "foo"

    def __init__(self):
        self.instance_var2 = "bar"


# ─── Interfaz ─────────────────────────────────────────────────────────────────

class InterfaceABC(abc.ABC):
    """Interface ABC."""

    @property
    @abc.abstractmethod
    def foo(self) -> str:
        ...