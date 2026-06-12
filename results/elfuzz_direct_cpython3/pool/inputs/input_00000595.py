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


def singleton(init_args: tuple[Any], init_kwargs: dict[str, Any]) -> type:
    """Decorator that returns a singleton instance of the decorated class."""
    return SingletonFactory(init_args, init_kwargs).create_instance()


# ─── Decorators ──────────────────────────────────────────────────────────────

def memoize(func):
    cache: dict[tuple[Any], Any] = {}
    @functools.wraps(func)
    def wrapped_func(*args):
        key = args
        if key in cache:
            return cache[key]
        r = func(*args)
        cache[key] = r
        return r
    
    return wrapped_func

memoized = memoize


def memoize_property(property):
    prop: property = property.fget

    @functools.wraps(prop)
    def get_memoized():
        if getattr(get            self.status = Status.RUNNING
        elif status == Status.SUCCESS:
            self.status = Status.SUCCESS
        else:
            raise ValueError(f"Invalid status: {status}")

    @property
    def history(self) -> list[Status]:
        return [*self._history]

    def merge(self, other: Task) -> Task:
        task = Task(
            id       = self.id,
            name     = self.name,
            priority = min(self.priority, other.priority),
            status   = self.status,
            tags     = sorted(set(list(self.tags) + list(other.tags))),
            metadata = {},
        )

        task.update_status(Status.SUCCESS)
        return task


def add_tags(task: Task, *tags: str) -> Task:
    task.tags.extend(tags)
    task.sort_key = hash(tuple(sorted(task.tags)))
    return task


def merge_tasks(tasks: list[Task]) -> Task:
    tasks.sort(key=lambda t: t.priority)
    
    res = tasks.pop(0).merge(tasks.pop(0))
    for task in tasks:
        res.merge(task)

    return res


# ── Generics ──────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)


class AbstractCollection(Generic[T_co]):
    async def add(self, item: T_co) -> None: ...
    async def pop(self) -> T_co: ...
    

