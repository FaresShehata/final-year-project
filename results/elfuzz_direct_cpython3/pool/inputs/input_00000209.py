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
    
    def __init__(self, func: Callable[[Self], T]) -> None:
        assert callable(func)
        
        self.func = func
        self.cache: WeakKeyDictionary[Object, T] = {}
        self.name: str = ""
    
    # noinspection PyAttributeOutsideInit
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"
    
    def __get__(self, instance: Object, owner: type) -> T:
        if instance is None:
            return self
        
        try:
            return self.cache.get(instance, None)
        except AttributeError:
            result = self.func(instance)
            self.cache[instance] = result
            return result


class ComparableMixin:
    """Mix-in class to provide comparison methods."""
    
    @classmethod
    @abc.abstractmethod
    def _compare(cls, other: Self, op: Callable[[Any, Any], bool]) -> bool:
        pass
    
    def __eq__(self, other: object) -> bool:
        return self._compare(other, operator.eq)
    
    def __lt__(self, other: object) -> bool:
        return self._compare(other, operator.lt)
    
    def __le__(self, other: object) -> bool:
        return self._compare(other, operator.le)
    
    def __ne__(self, other: object) -> bool:
        return self._compare(other, operator.ne)
    
    def __gt__(self, other: object) -> bool:
        return self._compare(other, operator.gt)
    
    def __ge__(self, other: object) -> bool:
        return self._compare(other, operator.ge)


# ─── MetaClasses ─────────────────────────────────────────────────────────────

# noinspection PyUnresolvedReferences,PyAbstractClass
class MyMeta(type):
    """A meta-class for our custom objects."""

    def __new__(
        cls,
        name: str,
        bases: tuple[type],
        attrs: dict[str, Any]
    ) -> MyMeta:
        print(f"Creating new class: {name}")
        return super().__new__(cls, name, bases, attrs)
    
    def __init__(self, name: str, bases: tuple[type], attrs: dict[str, Any]):
        print(f"Initializing class: {name}")
        super().__init