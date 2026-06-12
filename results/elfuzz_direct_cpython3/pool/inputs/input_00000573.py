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


# ─── Classes ──────────────────────────────────────────────────────────────────


def classproperty(func):
    """A class method decorator equivalent to @classmethod but for properties."""

    return classmethod(property(func))


@functools.lru_cache(maxsize=32)
class LazyClass:
    """Lazy evaluation of a class from its constructor arguments.

    Args:
        *args (Any): Constructor argument(s).
        **kwargs (Any): Keyword argument(s).

    Usage:

    >>> @lazyclass
    ... class Foo:
    ...     x: int
    ...     y: float
    ...
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> foo = Foo(42, 3.14)
    >>> foo.x
    42
    >>> foo.y
    3.14

    """

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

    def __new__(
        cls,
        *args: Any,
        wrapper: Optional[type] = None,
        **kwargs: Any,
    ) -> Type[LazyClass]:
        # We use the original class as the base so it inherits all class attributes.
        orig_cls = type(cls.__name__, (cls,), {})
        cls._base_attrs = set(orig_cls.__dict__.keys())

        def construct(*a, **k):
            return orig_cls(*a, **k)

        attrs = dict(wrapper or {})

        # This loop is necessary since when we call `super()`, we get an instance
        # of the base class instead of the actual class itself.
        for attr in reversed(cls.mro()):
            for key, value in attr.__dict__.items():
                if key in attrs:
                    continue
                elif (
                    hasattr(value, "__call__")
                    and key in cls._base_attrs
                    and issubclass(type(value), LazyClass)
                ):
                    attrs[key] = construct
                else:
                    attrs[key] = value

        new_cls = type(
            cls.__name__,
            (orig_cls,),
            {
                "__new__": staticmethod(lambda cls, *a, **k: object.__new__(orig_cls)),
                **attrs,
            },
        )

        # We want to make sure that the original class's superclass is still accessible.
        new_cls.__mro__ = list(new_cls.mro()) + [orig_cls]
        new_cls.__bases__ += tuple(new_cls.__mro__[:-1])
        return new_cls


def lru_cache(limit: int = 512):
    """LRU caching function decorator with limited size."""
    cache = {}

    def wrap(func):
        nonlocal limit

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = hash((func, args, kwargs))
            try:
                result = cache[key]
            except KeyError:
                result = func(*args, **kwargs)
                cache[key] = result
                if len(cache) >= limit:
                    del cache[next(iter(cache))]
            return result

        return wrapped

    return wrap


# ─── Metaclasses ─────────────────