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

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, "__%s__" % self.func.__name__)
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

    def __init__(self, value: T | Exception | None, tail: Trampoline | None = None):
        self.value = value
        self.tail = tail

    def unwrap(self) -> T:
        if isinstance(self.value, Exception): raise self.value
        elif self.tail is None: return self.value
        else: return self.tail.unwrap()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trampoline): return NotImplemented

        if self.value == other.value:           # same value?
            if self.tail is None:               # both are done?
                if other.tail is None:          # then both must be done too!
                    return True
                else:                           # but one is done and one isn't?
                    return False

            elif other.tail is None:            # both have tails? they must match!
                return Trampoline.is_done(self.tail) and Trampoline.is_done(other.tail)

            else:                               # both have tails, compare them recursively...
                return self.tail == other.tail
        else:
            return False

    @staticmethod
    def is_done(trampoline: Trampoline | None) -> bool:
        return trampoline is None or trampoline.tail is None

    @classmethod
    def from_exception(cls, exception: Exception) -> Trampoline[Exception]:
        return cls(exception)

    @classmethod
    def from_value(cls, value: T) -> Trampoline[T]:
        return cls(value)

    @classmethod
    def from_tail(cls, tail: Trampoline) -> Trampoline[None]:
        return cls(None, tail)

    @classmethod
    def from_lambda(cls, thunk: Callable[[Trampoline], Trampoline]) -> Trampoline[None]:
        return cls.from_tail(
            Trampoline.from_lambda(lambda _: Trampoline(thunk))

        )


def trampoline(func
def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
