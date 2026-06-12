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
        print("__get__")
        return f"Hello {self._name}"

    @name.setter
    def name(self, value: str) -> None:
        print("__set__")
        self._name = value

    @name.deleter
    def name(self) -> None:
        print("__del__")
        del self._name


'''
You can also use descriptor protocol directly if you need to do some kind of validation.
'''

class NameDescriptor:
    def __set_name__(self, owner_class: type, attr_name: str):
        self.attr_name = "_" + attr_name

    def __get__(self, obj: PersonWithSetter, cls: type[PersonWithSetter]) -> str:
        return getattr(obj, self.attr_name)

    def __set__(self, obj: PersonWithSetter, value: str) -> None:
        setattr(obj, self.attr_name, value.upper())


class PersonWithSetter:
    name = NameDescriptor()

    def __init__(self, name: str):
        self.name = name


'''
