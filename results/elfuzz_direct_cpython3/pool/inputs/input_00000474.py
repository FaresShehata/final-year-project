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


class CachedProperty(TypedDescriptor):
    """A property whose value is computed once per instance and then replaced."""
    
    def __init__(self, func):
        self.func = func
        self.name: str = ""
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val = obj.__dict__[self.name] = self.func(obj)
        return val


# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(type):

    def __prepare__(metacls, name, bases, **kwargs):  # type: ignore[misc]
        return {}

    def __new__(
            metacls,
            name: str,
            bases: tuple[type],
            namespace: dict[str, Any],
            **kwargs: Any,
    ) -> Type[T]:
        if "__module__" in namespace or "__qualname__" in namespace:
            del namespace["__module__"]
            del namespace["__qualname__"]

        if "__slots__" in namespace:
            slots = namespace.pop("__slots__")
            attrs = {}
            for attr in slots:
                attr = attr.strip()
                attrs[attr] = TypedDescriptor(TypeVar(attr))
            namespace.update(attrs)

        print(namespace)
        cls = super().__new__(metacls, name, bases, namespace)
        cls._registry = {}
        for base in reversed(bases):
            reg_cls = registry(base)
            if reg_cls is not None:
                cls._registry |= reg_cls._registry
        reg_cls = registry(cls)
        if reg_cls is not None:
            cls._registry |= reg_cls._registry
        return cls

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)
        key = (inst.__class__.__name__, inst.color)
        cls._registry[key] = inst
        return inst

    def __getitem__(cls, item):
        try:
            return cls._registry[item]
        except KeyError as exc:
<|file_sep|>/seed-06/shape.py
"""
Seed 05 - Decorators & Context Managers
"""


# ── Decorators ────────────────────────────────────────────────────────────────
def debug(func):
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        val = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {val!r}")
        return val

    return wrapper_debug

@debug
def add(x, y):
    return x+y

add(2,3)
<|file_sep|><|fim_prefix|>/seed-04/tests/test_shape.py
"""
Seed 04 - Generators & Iterators
"""


# ── Iterators ─────────────────────────────────────────────────────────────────

class StrIter:
    """
    An iterator over the characters of some string.
    """
    def __init__(self, s:str):
        self.data = s
        self.index = -1
    
    def __next__(self)->str:
        self.index += 1
        if self.index >= len(self.data):
            raise StopIteration()
        return self.data[self.index]
    
    def __iter__(self)->StrIter:
        return self
    



# ── Generators ─────────────────────────────────────────────────────────────────

def gen():
    for i in [1,2,3]:
        yield i

for n in gen():
    print(n)


g = gen()

print(next(g))
print(next(g))

print([n for n in g])


class GenIterator:
    """
    A generator that yields numbers between start (inclusive) and end (exclusive).
    """

    def __init__(self, start:int, end:int):
     <|fim_suffix|>   else:
                break

    def __iter__(self):
        return self

try:
    it = GensIter(1,2)
    print(list(it))
except Exception as exc:
    print(exc)



# ── Context Manager ───────────────────────────────────────────────────────────

class FileContextMgr(object):
    def __enter__(self            raise KeyError(f"No such shape: {item}") from exc

    def __iter__(cls):
        return iter(cls._registry.values())

    def __len__(cls):
        return len(cls._registry)

    def __contains__(cls, item):
        return any(item == k for k in cls._
def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

