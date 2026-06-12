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
    """

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance._state = _State(instance)
        instance._state.set_args(*args, **kwargs)
        return instance

    def __getattr__(self, attr):
        state = getattr(self._state, "state", None)
        if state is not None:
            return getattr(state, attr)
        raise AttributeError(attr)

    def __setattr__(self, attr, val):
        # Prevent the user from setting attributes on instances.
        raise NotImplementedError

    def __delattr__(self, attr):
        # Prevent the user from deleting attributes on instances.
        raise NotImplementedError

    def __dir__(self):
        state = getattr(self._state, "state", None)
        attrs = dir(type(self)) + list(dir(super()))
        if state is not None:
            attrs += [f"-{a}" for a in state.state_attributes]
        return sorted(set(attrs))

    def __repr__(self):
        cls = type(self).__qualname__
        args = ", ".join(str(getattr(self, a)) for a in dir(type(self)))
        return f"<{cls}({args})>"

    def __eq__(self, other):
        return (
            type(other) == type(self)
            and all(getattr(self, a) == getattr(other, a) for a in dir(type(self)))
        )

    def __hash__(self):
        return hash((type(self), tuple(getattr(self, a) for a in dir(type(self)))))


