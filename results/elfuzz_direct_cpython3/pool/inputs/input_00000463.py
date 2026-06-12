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
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
            raise ValueError(f"{value} out of bounds [{self.lo}, {self.hi}]")
        
        setattr(instance, self.name, value)

    def __get__(self, instance: T, owner: type[T]) -> Any:
        return getattr(instance, self.name)


# ─── INHERITANCE, SUBCLASSES AND SLOTS ───────────────────────────────────────

class BaseClassA(metaclass=abc.ABCMeta):
    """Abstract base class that defines an abstract method."""

    @property
    @abc.abstractmethod
    def a_attr(self) -> int:
        ...

    def print_a_attr(self) -> None:
        print(self.a_attr)



class BaseClassB(BaseClassA):
    """Base class with an attribute that needs to be initialized via the setter."""

    b_attr: float = 0.0

    def __init__(self) -> None:
        self.b_attr = 1.0


class BaseClassC(BaseClassB):
    """Base class with an attribute that can only be set once during initialization."""

    c_attr: complex = 0j

    def __init__(self) -> None:
        super().__init__()
        self.c_attr = 1j



class BaseClassD(BaseClassC):
    """Base class with a read-only property."""

    d_attr: str = ""

    @property
    def d_attr(self) -> str:
        return self._d_attr
    
    @d_attr.setter
    def d_attr(self, value: str) -> None:
        self._d_attr = value



class BaseClassE(BaseClassD):
    pass


# ─── PROPERTY ────────────────────────────────────────────────────────────────

class PropertyExample:
    def get_a_property(self) -> int:
        return self._a_property

    def set_a_property(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Value must be an integer.")
        self._a_property = value

    a_property: property = property(get_a_property, set_a_property)




# ─── COMPOSITION OF CLASSES ──────────────────────────────────────────────────

class A:
    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"A({self.value})"

    def __str__(self) -> str:
        return f"Instance of A with value {self.value}"


class B(A):
    def __init__(self, value: int) -> None:
        super().__init__(value=value * 2)


class C(B):
    def __init__(self, value: int) -> None:
        super().__init__(value=value * 3)


# ─── EXTENSION OF CLASSES ─────────────────────────────────────────        repr_str = f"{self.__class__.__name__}"
        for attr in dir(self):
            if not attr.startswith("__"):
                val = getattr(self, attr)
                repr_str += f"\n\t{name}={val}"
        return repr_str


class ConcreteClassA(BaseClassA):
    _a_attr: int = 42
    b_attr: float = 3.14
    c_attr: complex = 1j + 1j
    d_attr: str = "foo"


# ─── METACLASS ───────────────────────────────────────────────────────────────


def meta_factory(name, bases, attrs) -> type[Any]:
    """A factory function for creating new metaclasses."""
    attrs["hello"] = "world!"
    return type(name, bases, attrs)


# ─── STATIC AND CLASS METHODS ────────────────────────────────────────────────

class StaticExample:
    cls_var: staticmethod[int] = staticmethod(lambda x: x ** 2)
    obj_var: methodcaller("func") = lambda self, x: x * 5


@functools.cache
def memoized_func(x: int) -> int:
    return x**2


@contextlib.contextmanager
def open_file(filename: str, mode="r") -> Iterator[None]:
    try:
        file = open(filename, mode)
        yield
    finally:
        file.close()



# ─── GENERATORS ──────────────────────────────────────────────────────────────