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

def registry(cls: T) -> Optional[Type[T]]:
    if not hasattr(cls, "_registry"):
        return None
    return cls._registry.get(cls.__name__)


class Base(metaclass=RegistryMeta):
    pass


class A(Base):
    pass


class B(Base):
    pass


class C(A):
    pass


node1 = A()
node2 = A()

print(node1 == node2)     # True
print(isinstance(node1, A))       # True
print(isinstance(node1, B))       # False
print(isinstance(B(), A))         # True
print(issubclass(A, Base))        # True
print(issubclass(Vertex, Base))   # True


class BSub(B):
    pass


b_sub = BSub()
print(isinstance(b_sub, B))      # True
print(isinstance(b_sub, BSub))   # True
print(isinstance(b_sub, Base))   # True
print(isinstance(b_sub, A))      # False
print(issubclass(BSub, B))       # True
print(issubclass(BSub, Base))    # True
print(issubclass(BSub, A))       # False


class CSub(C):
    pass


c_sub = CSub()
print(isinstance(c_sub, Base))          # True
print(isinstance(c_sub, C))             # True
print(isinstance(c_sub, CSub))          # True
print(isinstance(BSub(), Base))          # True
print(isinstance(BSub(), C))             # False
print(isinstance(BSub(), CSub))          # True
print(isinstance(CSub(), Base))          # True
print(isinstance(CSub(), C))             # True
print(isinstance(CSub(), CSub))          # True
print(isinstance(CSub(), A))             # False
print(isinstance(CSub(), B))             # False
print(isinstance(BSub(), A))             # False
print(isinstance(BSub(), B))             # True
print(issubclass(CSub, Base))           # True
print(issubclass(CSub, C))              # True
print(issubclass(CSub, CSub))           # True
print(issubclass(CSub, A))              # False
print(issubclass(CSub, B))              # False
print(issubclass(CSub, BSub))           # True
print(issubclass(BSub, Base))           # True
print(issubclass(BSub, C))              # False
print(issubclass(BSub, CSub))           # False
print(issubclass(BSub, A))              # False
print(issubclass(BSub, B))              # True
print(issubclass(BSub, BSub))
c = C()


print(c.__mro__)
print(registry(C))

# ── Context Manager ──────────────────────────────────────────────────────────
@contextlib.contextmanager
def my_context_manager():
    try:
        yield
    finally:
        print('goodbye')


with my_context_manager() as a, my_context_manager() as b:
  <|file_sep|>/seed-03/inheritance.py
import unittest
from graph import Graph
from shape import Shape, Circle
from vertex import Vertex
from edge import Edge

class TestVertex(unittest.TestCase):
    def test_node(self):
        g = Graph(4)
        n1 = Node(g, 0)
        n2 = Node(g, 1)
