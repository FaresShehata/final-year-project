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

    def __get__(self, obj, cls):
        return getattr(obj, f"_{cls.__name__}__{self.name}")

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{obj} must be {self.expected_type}")
        if self.lo is not None and value < self.lo:
            raise ValueError(
                f"value below minimum ({self.lo}) for descriptor {self}"
            )
        if self.hi is not None and value > self.hi:
            raise ValueError(
                f"value above maximum ({self.hi}) for descriptor {self}"
            )
        setattr(obj, f"_{cls.__name__}__{self.name}", value)

    def __delete__(self, obj):
        delattr(obj, f"_{obj.__class__.__name__}__{self.name}")


def Typed(expected_type, lo=None, hi=None):
    """Class decorator that applies a typed descriptor to all non-special methods."""

    def decorate(cls):
        for attr in cls.__dict__.values():
            if isinstance(attr, property):
                continue
            if (
                not hasattr(attr, "__get__")
                and not hasattr(attr, "__set__")
                and not hasattr(attr, "__delete__")
            ):
                setattr(cls, attr.__name__, TypedDescriptor(expected_type, lo=lo, hi=hi))
        return cls
    return decorate


# ── Metaclasses ───────────────────────────────────────────────────────────────

class StructMeta(type):
    """Metaclass for NamedTuple-like classes that allows defining fields using __annotations__."""

    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __new__(metacls, name, bases, namespace):
        annotations = getattr(namespace, '__annotations__', {})
        slots = [k for k, v in annotations.items() if isinstance(v, tuple)]
        namespace['__slots__'] = slots + ["_state"]
        namespace['_fields'] = tuple(k for k in annotations.keys() if k not in slots)
        state_fields = ", ".join(f"_field{i}: Any" for i in range(len(slots)))
        init_args = ', '.join(f'arg{i}' for i in range(len(slots)))
        namespace['__init__'] = types.MethodType(
            lambda cls, self, *args, **kwargs:
            setattr(self, "_state", {**            return getattr(obj, "__%s__" % self.func.__name__)
        except AttributeError:
            val = self.func(obj)
            setattr(obj, "__%s__" % self.func.__name__, val)
            return val


class DefaultFactory(abc.ABC):

    def __call__(self, *args, **kwargs) -> Any:
        """Create a default instance of this factory's class."""
        cls = type(self)
        return cls.default(*args, **kwargs)


class Singleton(DefaultFactory):

    _instances: dict[type, type] = {}

    def __new__(cls, *args, **kwargs) -> Singleton:
        if cls in cls._instances.values():
            return cls._instances[cls]
        inst = super().__new__(cls, *args, **kwargs)
        cls._instances[cls] = inst
        return inst


class WeakSingleton(Singleton):
    """A singleton whose instances are kept track of by a weak reference.

    A weak singleton can outlive its original owner. For example:

      >>> class Foo:
      ...     x = WeakSingleton()

      >>> foo = Foo()
      >>> del foo
      >>> print(Foo.x)
      <weakref at 0x...; dead>
    """

    def __reduce__(self):
        return (super().__reduce__, (type(self),))


class SingletonDefault(DefaultFactory):
    """A default factory that returns an existing singleton instance."""

    _instances: dict[Any, Any] = {}
    _types: dict[Any, set[type]] = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        SingletonDefault._types.setdefault(cls, set())
        SingletonDefault._types[cls].add(type(cls))

    def __new__(cls, *args, **kwargs) -> SingletonDefault:
        if len(args) != 1 or kwargs:
            raise TypeError("__init__ takes exactly one positional argument")
        key = args[0]

        if key is None:
            for typ in SingletonDefault._types.get(cls, ()):
                if cls in typ._instances:
                    return typ._instances[cls]
            inst = super().__new__(cls)
            cls._instances[key] = inst
            return inst

        if key not in cls._instances:
            for typ in SingletonDefault._types.get(cls    """Trampoline: a data structure that represents an operation on a Maybe monad.
       The Maybe monad can be used to represent side-effects or errors without
       changing the core algorithm."""

    __slots__ = ("value", "tail")

