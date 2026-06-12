"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import dataclasses
import datetime
import enum
import functools
import inspect
import itertools
import logging
import operator
import pathlib
import random
import re
import sys
import timeit
import typing
import uuid


if sys.version_info < (3, 9):
    raise RuntimeError("requires Python >= 3.9")


# -------------------------------------------------------------------------------------------------
# types and classes
# -------------------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Person:
    name: str = ""
    age: int = 0


def _get_person(name: str) -> Person | None:
    # only for testing purposes
    return {
        "John": 27,
        "Jane": 28,
    }.get(name)


# -------------------------------------------------------------------------------------------------
# classes with properties
# -------------------------------------------------------------------------------------------------

'''
Properties are used to encapsulate data access in a class.
They allow you to control how attributes are accessed and modified.

Note that property is not the same as descriptor.

A descriptor is an object that defines one or more of the following methods:

__get__()
__set__()
__delete__()

Property is similar to descriptor but it's easier to use.


Decorator @property allows you to define getter method on the fly by using a function.
'''


class PersonWithGetter:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        print("called getter")
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        print("called setter")
        self._name = value

    @name.deleter
    def name(self):
        print("called deleter")
        del self._name


p1 = PersonWithGetter("Alice")
print(p1.name)

try:
    p1.name = 42
except Exception as e:
    print(e.args[0])

del p1.name


# -------------------------------------------------------------------------------------------------
# abstract base class
# -------------------------------------------------------------------------------------------------

'''
Abstract Base Class can be inherited from other classes.
It's useful when we want to enforce certain rules for our subclasses.

By defining abstract methods, we can ensure that subclasses provide specific implementations of those methods.
This helps maintain consistency across related classes and prevents errors due to missing or incorrect behavior.
'''

# example class


@dataclasses.dataclass(frozen=True)
class ShapeABC(abc.ABC):
    """Abstract Base Class"""

    name: str = ""

    @classmethod
    @abc.abstractproperty
    def area(cls) -> float:
        """area of shape"""
        pass

    @abc.abstractmethod
    def draw(self) -> None:
        """draws the shape"""
        pass


# example subclass


@dataclasses.dataclass(frozen=True)
class Circle(ShapeABC):
    radius: float = 0

    # decorator @property is used here because we need to get the value of area before drawing circle
    @property
    def area(self) -> float:
        return math.pi * self.radius ** 2

    def draw(self):
        print(f"circle drawn with radius {self.radius}")


c = Circle(radius=5)
print(c.area)
c.draw()


# -------------------------------------------------------------------------------------------------
# metaclass
# -------------------------------------------------------------------------------------------------

'''
Metaclasses are special classes that create and control classes.
In Python, every class has a metaclass associated with it, which is responsible for creating and managing instances of that class.
The default metaclass in Python is type, which creates new types dynamically at runtime.
You can also define your own metaclasses to customize class creation behavior.
'''


def my_metaclass(meta_cls):
    """decorator to mark a class as metaclass"""

    def wrapper(klass):
        klass.__metaclass__ = meta_cls
        return klass