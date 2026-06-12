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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(
                f"Got {val!r}, which exceeds the range ({self.hi}) """
                            "(inclusive)"
                        )
        setattr(obj, self.name, val)


# ─── Decorators ──────────────────────────────────────────────────────────────

def classproperty(method: Callable[[Type[T]], T]) -> ClassPropertyDescriptor[T]:
    """
    A decorator for defining read-only properties on classes.
    This property can only be set once. After this point, it will always return whatever value was previously assigned to it.

    Args:
        method (Callable[[Type[T]], T]): The function encapsulating logic for the property's getter.

    Returns:
        ClassPropertyDescriptor[T]: A descriptor object representing the class property.
    """

    @functools.wraps(method)
    def get(self):
        if hasattr(self, "_clsprop_cache"):
            return self._clsprop_cache
        else:
            value = method(self)
            setattr(self, "_clsprop_cache", value)
            return value

    return property(get)


def memoize_method(method: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator for caching the results of the decorated method for each instance it is called on.

    Args:
        method (Callable[..., Any]): The function to decorate.

    Returns:
        Callable[..., Any]: The wrapped function with caching capabilities.
    """
    cache_key = _cache_key(method)

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        key = tuple(args), frozenset(kwargs.items())

        try:
            return cache[key]
        except KeyError:
            value = cache[key] = method(*args, **kwargs)
            return value

    wrapper.clear_cache = lambda: cache.pop(key, None)
    wrapper.cache_clear = lambda: cache.clear()

    return wrapper


class CacheWrapper(metaclass=abc.ABCMeta):
    """
    Wraps a callable and caches its results using a WeakKeyDictionary.
    This allows the cache to automatically remove entries when their associated objects are garbage collected.
    """

    def __init__(self, fn: Callable[..., Any]):
        self.fn = fn
        self.cache = weakref.WeakKeyDictionary()

    def __call__(self, *args, **kwargs):
        return self.cache[args]

    def clear_cache(self):
        self.cache.clear()


def memoized_property(fn: Callable[..., T]) -> PropertyWrapper[T]:
    """
    A decorator for creating a cached property.
    When accessed for the first time, the underlying function `fn` is executed and its return value is stored        return getattr(obj, self.name, None)

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
            
        except KeyError as e:
            result = self.func(instance)
            self.cache[e.value] = result
            return result


# ─── Context Managers ────────────────────────────────────────────────────────

@contextlib.contextmanager
def append_list(l: list[Any]) -> Iterator[list[Any]]:
    l.append(sys.exc_info())
    yield l
    del l[-1]


with append_list([]) as l:
    print(l)
    x = 1 / 0
    
    print(l)
    

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class SuppressOutputManager:
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_stdout_output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout
        return False


with SuppressOutputManager() as s:
    print(s)
    x = 1 / 0
    

class SuppressOutputContext(ContextDecorator):
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_stdout_output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout
        return False

 
SOMETHING_TO_SUPPRESS_OUTPUT_INTO = object()


class SuppressOutput(SuppressOutputContext):
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout

        if SOMETHING_TO_SUPPRESS_OUTPUT_INTO in locals():
            locals()[SOMETHING_TO_SUPPRESS_OUTPUT_INTO].append(output)
