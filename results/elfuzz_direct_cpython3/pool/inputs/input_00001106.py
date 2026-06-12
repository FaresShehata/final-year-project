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
                f"Got {val!r}, which exceeds the range ({self.hi}) "
            )

        setattr(obj, self.name, val)


def typed(name: str) -> type:
    """
    Returns a new descriptor class with a single attribute named after self.

    The attribute is set by setting an instance of this descriptor on the target
    object. This can be done using the dot notation, or through calling it as a
    function (and passing the instance as first argument).

    >>> from pprint import pprint
    >>>
    >>> class Foo(object):
    ...     bar = typed('bar')
    ...
    >>>
    >>> pprint(Foo.bar)
    <some random object>

    If one wants to enforce specific values, they need to define the attributes
    `lo` and `hi`, e.g.

    >>> class Bar(object):
    ...     baz = typed('baz', lo=3, hi=7)
    ...
    >>>
    >>> pprint(Bar.baz)
    <some random object>
    """

    self = TypedDescriptor()
    self.name = ""
    return self


class TypedGenericMeta(type):
    def __new__(mcls, name, bases, namespace):

        attrs = {
            attr: TypedDescriptor() for attr in namespace.keys()
            if not attr.startswith("_")
        }
        return super().__new__(mcls, name, bases, namespace.update(attrs))


class TypedGeneric(metaclass=TypedGenericMeta):
    ...


# ── Context manager ───────────────────────────────────────────────────────────

@contextlib.contextmanager
class ContextManager:
    def __init__(self, value: bool = False) -> None:
        self.value = value
    
    @classmethod
    def wrap(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ctx_mgr = cls()

            try:
                yield ctx_mgr
                func(*args, **kwargs)
            finally:
                ctx_mgr.value = True
        
        return wrapper

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# ─── Meta classes ─────────────────────────────────────────────────────────────

class SingletonMetaClass(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        
        return cls._instances[cls]


class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        
        return cls._instance


class SingletonFactory(metaclass=SingletonMetaClass):
    def __init__(self, init_args: tuple[Any], init_kwargs: dict[str, Any]):
        self.init_args = init_args
        self.init_kwargs = init_kwargs

    def create_instance(self) -> Any:
        return type("", (), {})(*self.init_args, **self.init_kwargs)

    def get_instance(self):
        return getattr(self, "instance", None) or self.create_instance()


class SingletonFactoryType(metaclass=SingletonType):
    pass


# ── Decorators ────────────────────────────────────────────────────────────────

def docstring_decorator(docstr: str) -> Callable[[Any], Any]:
    def inner(f: Callable[..., Any]) -> Any:
        f.__doc__ = docstr
        return f
    return inner


def debug_mode():
    __debug__: bool = True

    # We do NOT want to have side effects here.
    # Thus, we use this trick so that the decorator
    # does NOT change the signature of the decorated
    # function's parameters.
    def outer_wrapper(func):
        argspec = inspect.getfullargspec(func)

        @functools.wrap(func)
        def wrapped_func(*args, **kwargs):
            nonlocal __debug__
            
            if __debug__:
                print(f"{func.__qualname__}: called with arguments:")
                print(args, kwargs)
                
            result = func(*args, **kwargs)
            
            if __debug__:
                print(result)
            
            __debug__ = False
            
            return result
        
        return wrapped_func

    return outer_wrapper


def memoize(f):
    cache = {}
    
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        key = repr((args, frozenset(kwargs.items())))
        
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        
        return cache[key]
    
    return wrapper


def memoize_property(prop):
    v = prop.fget(instance)
    
    @property.setter
    def setter(self, value):
        self.__dict__[prop.fget.__name__] = value
        

def cached_property(property):
    pass


# ─── Generators ──────────────────────────────────────────────────────────────

def fib(max=1_000):
    n, m = 0, 1
    
    while n <= max:
        yield n
        n, m = m, m + n