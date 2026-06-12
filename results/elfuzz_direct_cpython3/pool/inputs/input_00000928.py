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
    def get_registry(cls) -> dict[str, type]:
        return cls._registry.copy()


# ── Abstract classes ──────────────────────────────────────────────────────────

class AbstractClassABC(abc.ABC):

    """Abstract class using ABCMeta which has no methods of its own."""

    pass


@RegistryMeta.register
class ConcreteDerived(AbstractClassABC):

    """Concrete subclass of an abstract base class."""

    pass


@RegistryMeta.register
class AnotherConcreteDerived(AbstractClassABC):

    """Another concrete subclass of an abstract base class."""

    pass


# ── Class decorator example ───────────────────────────────────────────────────

def debug_all(func: Callable[..., T], *, prefix="debug_"):
    """
    Decorate functions by adding debugging statements around them.

    Args:
      prefix (str): Prefix for the generated debugging statement(s). Defaults to "debug_".
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(prefix + func.__name__)
        result = func(*args, **kwargs)
        print(prefix + func.__name__, "->", result)
        return result
    return wrapper


# ── Context manager example ────────────────────────────────────────────────────

@contextlib.contextmanager
def open_read(path: str) -> Generator[IO[Any], None, None]:
    try:
        file_handle = open(path, 'rt')
        yield file_handle
    finally:
        file_handle.close()
    

@contextlib.contextmanager
def open_write(path: str) -> Generator[IO[Any], None, None]:
    try:
        file_handle = open(path, 'wt')
        yield file_handle
    except Exception as e:
        print(e)
    finally:
        file_handle.close()        


# ── Generators ─────────────────────────────────────────────────────────────────

def take(iterable: Iterable[T], n: int) -> Generator[T, None, None]:
    """Return first n items from the iterable."""
    return itertools.islice(iterable, n)

def distinct(iterable: Iterable[T]) -> Generator[T, None, None]:
    """Return unique elements in order preserving way."""
    seen: set[T] = set()
    for x in iterable:
        if x in seen:
            continue
        yield x
        seen.add(x)

def count_cond(p: Callable[[T], bool]) -> Callable[[Iterable[T]], int]:
    """Returns function counting how many times p returns True for its arguments."""
    
    def count(xs: Iterable[T]):
        return sum(map(p, xs))
    return count


def timed_execution(func: Callable[..., T], *args, **kwargs) -> float:

    """Execute function and time it. Return time in seconds."""
    
    t_start = time.time()
    output = func(*args, **kwargs)
    t_finish = time.time()
    return t_finish - t_start
    
    
# ── Functions ──────────────────────────────────────────────────────────────────

def memoize(func: Callable[..., T]) -> Callable[..., T]:

    """Memoize a callable so that results are stored for future calls."""
    
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args + tuple(kwargs.items())
        if key not in        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
