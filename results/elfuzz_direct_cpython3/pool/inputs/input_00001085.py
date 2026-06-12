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

    def __init__(self, func): # pylint: disable=super-init-not-called
        self.func = func
        self.name: str = ""
        self.weakref_cache: bool = False

    def __call__(self, instance):
        return self.__get__(instance, instance.__class__)

    def __get__(
        self,
        instance,
        owner
    ) -> Any:
        try:
            return instance.__dict__[self.name]
        except KeyError:
            pass
        else:
            if self.weakref_cache:
                del instance.__dict__[self.name]

        result = value = self.func(instance)
        instance.__dict__[self.name] = value
        return result


# ─── Decorators ──────────────────────────────────────────────────────────────

def typed(*types):
    """Decorator for defining typed properties."""
    assert len(types) > 0
    if any(not isinstance(t, (type, tuple)) for t in types):
        raise TypeError("all arguments must be either type or tuple of types")
    elif len(types) == 1:
        t = types[0]
        if isinstance(t, tuple):
            types = t
        else:
            types = (t,)
    ret = [TypedDescriptor(t) for t in types]
    return functools.cached_property(lambda cls: _typed_property(cls, *ret))


@functools.cache
def _typed_property(owner, *descs):
    prop = property(**{d.name: d for d in descs})
    return property(lambda x: prop(x), lambda x: prop.fset(x, prop.fget(x)))


def classproperty(func):
    """Define a class property.

    Example:

    ```python
    @classmethod
    def foo(cls):
        ...

    Foo.foo: Callable[[Type[Foo]], T]
    ```

    This allows the function to be called as:

    ```python
    Foo.foo()
    ```
    """
    if not hasattr(type, "__annotations__"):
        raise AttributeError("__annotations__ is missing from the type object.")

    return classmethod(property(func))


def check_types(f):
    """Check for mismatched argument types.

    Example:
    ```python
    >>> @check_types
    ... def add(a: int, b:int)->int:
    ...     return a + b
    ...
    >>> isinstance(add(3, "4"), int)
    True
    >>> add(3, "4")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/martin/Projects/python-tutorial/oop/clean-code.py", line 65, in add
        raise TypeError(f"expected {a!r} + {b!r} but got {c!r}")
    TypeError: expected '3' + '4' but got ''
    ```
    """

    def wrapper(self, *args, **kwargs):
        argspec = inspect.getfullargspec(f)
        sig = inspect.Signature.from_callable(f)

        params = dict(zip(sig.parameters, args))
        params.update(kwargs)

        bound_args = sig.bind_partial(*args, **kwargs).arguments
        unbound_args = sig.parameters.keys() - bound_args.keys()

        if (len(unbound_args) != 0) ^ (any(isinstance(p.annotation, type)# ── Async machinery ───────────────────────────────────────────────────────────

