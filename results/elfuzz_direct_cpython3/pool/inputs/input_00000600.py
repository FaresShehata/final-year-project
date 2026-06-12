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

    @classmethod
    def get_cls(mcs, name: str) -> Optional[Type]:
        try:
            return mcs._registry[name]
        except KeyError:
            return None


def inspect_abstract(cls: Type[T]) -> bool:
    return cls in [AbstractBaseClass, AbstractConcreteClass]


class AbstractBaseClass(metaclass=RegistryMeta):
    """Marker base class for all abstract classes."""

    pass


class AbstractConcreteClass(AbstractBaseClass):
    """Marker subclass for concrete classes."""


# ─── Generators ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def temporary_file(name: str, contents: str) -> Generator[str, None, None]:
    with open(name, "w") as file_:
        yield file_.write(contents)


def fibonacci(n: int) -> Iterator[int]:
    x, y = 0, 1
    for i in range(n):
        yield x
        x, y = y, x + y


# ─── Context Manager ──────────────────────────────────────────────────────────

FAKE_FILE_OBJ = object()


@contextlib.contextmanager
def fake_open() -> Generator[tuple[Any], None, None]:
    """Context manager that returns an object instead of opening files."""
    yield FAKE_FILE_OBJ


# ─── Decorators ───────────────────────────────────────────────────────────────

@functools.wraps(print)
def my_print(*args, sep=" ", end="\n", flush=False, **kwargs) -> None:
    """Prints formatted string to stdout.

    Serves as a decorator.
    """
    print(sep.join(map(str, args)), end=end, flush=flush, **kwargs)


def log_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator which logs the function being called.

    Args:
        func (Callable[..., T]): Target function.

    Returns:
        Callable[..., T]: New function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("%r(%r)", func, args)
        result = func(*args, **kwargs)
        logging.info("\treturning %r", result)
        return result

    return wrapper


# ─── Clases ───────────────────────────────────────────────────────────────────

class MyEnum(Enum):
    """An enum-like class."""

    A = auto