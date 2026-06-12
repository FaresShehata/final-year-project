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


class Integer(TypedDescriptor):
    pass


class FloatRange(TypedDescriptor):
    pass


class String(TypedDescriptor):
    pass


Integer.TYPE_NAME = "an integer"
String.TYPE_NAME = "a string"


class ExampleClass:
    x: Integer = Integer(Integer.TYPE_NAME)
    y: FloatRange(5.0, 7.8)
    z: Optional[String] = None


# ── Metaclasses ───────────────────────────────────────────────────────────────

class Meta(type):
    # This class doesn't do much.
    pass


class MyMeta(MyMeta):

    @classmethod
    def __prepare__(metacls, cls, bases):
        print("__prepare__")
        return {}

    @classmethod
    def __new__(mcs, name, bases, namespace):
        print("__new__")
        return super().__new__(mcs, name, bases, namespace)

    @classmethod
    def __init__(cls, name, bases, namespace):
        print("__init__")


class MyClass(metaclass=MyMeta):
    ...


class Singleton(type):
    _instances: dict[type, object] = {}

    @classmethod
    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            return cls._instances[cls]
        instance = super(Singleton, cls).__call__(*args, **kwargs)
        cls._instances[cls] = instance
        return instance


@contextlib.contextmanager
def something():
    try:
        yield
    except Exception as e:
        print(e)


class SomethingElse:
    ...


@contextlib.contextmanager
def context_manager(something_else, some_value):
    try:
        yield something_else
    finally:
        print(some_value)


class SomeBaseType:
    ...


class SomeOtherBaseType:
    ...


class AnotherDerivedClass(SomeBaseType, SomeOtherBaseType):
    ...


class BaseClass:
    @property
    def thing(self):
        return 42

    @thing.setter
    def thing(self, new_thing: int):
        self.thing = new_thing + 1


class DerivedClass(BaseClass):
    pass


class TestContextManager:
    def test_context_manager(self):
        with context_manager(SomethingElse(), "something else") as smth:
            assert sm