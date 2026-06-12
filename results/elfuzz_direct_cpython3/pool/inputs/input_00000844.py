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

    def __delattr__(cls, item):
        del cls._instance


# ─── Generators ───────────────────────────────────────────────────────────────

def make_generator(args: tuple[Any], kwargs: dict[str, Any]) -> Callable[..., Generator]:
    @functools.wraps(make_generator)
    def generator():
        yield from args
        yield from (
            [k + v for k, v in kwargs.items()]
        )

    return generator()


if __name__ == "__main__":
    print(sys.version_info)



# ─── Classes ──────────────────────────────────────────────────────────────────

class MyClass:
    def __init__(self, x: int = 42, y: float = 3.14) -> None:
        self.x = x
        self.y = y

    def greet(self) -> str:
        return f"Hello, I'm {self.x}."


class MySubclass(MyClass):
    def say_hi(self) -> str:
        return f"Hey, you're {self.y}"



# ─── Mixin classes ────────────────────────────────────────────────────────────

class MyMixin:
    def __repr__(self):
        return f"{type(self).__name__}(x={self.x}, y={self.y})"

    @property
    def xy(self) -> tuple[int, float]:
        return self.x, self.y

    @xy.setter
    def xy(self, value: tuple[int, float]):
        self.x, self.y = value

    @staticmethod
    def static_method(x: int = 0, y: int = 0) -> None:
        print(f"x:{x}, y:{y}")

    @classmethod
    def class_method(cls, x: int = 0, y: int = 0) -> None:
        print(f"x:{x}, y:{y}")

    @property
    def area(self) -> int:
        return abs(self.x - self.y)

    @area.setter
    def area(self, value: int) -> None:
        self.x = value / 2
        self.y = value / 2





# ─── Classes ──────────────────────────────────────────────────────────────────

class MyDecorator:
    def __init__(self, func) -> None:
        self.func = func
    
    def __call__(self, *args, **kwargs):
        self.func(*        self.init_kwargs = init_kwargs

    def create_instance(self) -> Any:
        return type("", (), {})(*self.init_args, **self.init_kwargs)


