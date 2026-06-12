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
                f"{obj} must be {self.expected_type} but got {value}."
            )
        if self.lo is not None and value < self.lo or self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name} must lie between {self.lo} and {self.hi}")
        setattr(obj, self.name, value)

    def __delete__(self, obj):
        delattr(obj, self.name)

class ReadableTypedDescriptor(TypedDescriptor):

    def __get__(self, obj, objtype=None):
        try:
            return super().__get__(obj, objtype=objtype)
        except AttributeError as e:
            if hasattr(obj, "is_readonly") and obj.is_readonly:
                raise PermissionError(f"{e.args[0]} - Cannot set read-only")
            raise

class IntegerReadDescriptor(ReadableTypedDescriptor[int]):
    def __init__(self, lo: int | None = None, hi: int | None = None):
        super().__init__(int=lo, hi=hi)

    def __set__(self, obj, value):
        if isinstance(value, float):
            value = round(value)
        if not isinstance(value, int):
            raise TypeError(f"{value} must be an integer.")
        return super().__set__(obj, value)

class PositiveIntegerReadDescriptor(IntegerReadDescriptor):
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError("Must be positive.")
        return super().__set__(obj, value)



# ─── Example Usage ────────────────────────────────────────────────────────────

class Point:

    x: int = IntegerReadDescriptor(-2 ** 30, 2**30-1)
    y: int = IntegerReadDescriptor(lo=-2 ** 30, hi=2**30-1)

    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
print(p.x, p.y)
try:
    # This should error out since we can't have negative coordinates.
    p.x = -1
except Exception as e:
    print(e)

# Now let's say I want to make coordinates readonly.
class ConstantPoint(Point):
    is_readonly = True

cp = ConstantPoint(x=1, y=2)
try:
    cp.x += 5
except Exception as e:
    print(e)

# Next up are @property decorators.

class Person:
    age: int = IntegerReadDescriptor()

    @property
    def is_adult(self) -> bool:
        return self.age >= 18

@contextlib.contextmanager
def open_file(filename: str, mode="r", encoding="utf-8"):
    file = open(filename, mode, encoding=encoding)
    yield file
    file.close()
    
with open_file("./test.txt", "w+") as file:
    file.write("Hello, world!")

# And now some metaclass stuff. The idea of a metaclass is to do similar things
# to what classes do, but at the higher level. For example, instead of writing 
# class MyClass(BaseClass): pass you would just write MyMetaClass = MyMetaclass(MyBaseClass). 

class BaseMeta(type):
    def __new__(cls, clsname, bases, attrs):
        for attr in attrs.keys():
            if callable(attr):
                attrs[attr] = wrap_method(clsname, attr)
        return super().__new__(cls, clsname, bases, attrs)

def wrap_method(clsname: str, method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        print(f"{clsname}.{method.__name__}: {args}, {kwargs}")
        return method(*args, **kwargs)
    return wrapper

class Base(metaclass=BaseMeta):
    def foo(self, arg1, arg2):
        return arg1 + arg2
    
    def bar(self, arg1, arg2):
        return arg1 * arg2

b = Base()
b.foo(1, 2)
b.bar(1, 2)

# We're going to use this pattern again for our decorator below.


# ─── Decorators ──────────────────────────────────────────────────────────────
def log_methods(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        print(result)
        return result
    return wrapped


# Now that we've