"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
from typing import Any, Callable, Generic, Iterable, Iterator, TypeVar


# ─── DESCRIPTION ────────────────────────────────────────────────────────────────


"""This is the first seed. It contains three sections:

- Section 1 describes how to use object-oriented programming.
- Section 2 introduces metaclasses.
- Section 3 shows how to use descriptors.


These are all part of the course's Object-Oriented Programming lesson.

"""


# ─── SECTION 1: OBJECT-ORIENTED PROGRAMMING ────────────────────────────────────


class Person:
    """A person, with name and age attributes."""

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


p: Person = Person("John Doe", 42)


# ─── SECTION 2: METACLASSES ────────────────────────────────────────────────────


class Meta(type):
    """Metaclass for testing purposes."""

    def __new__(
        metacls: type, classname: str, bases: tuple[type], namespace: dict[str, Any]
    ) -> type:
        print(
            f"Creating new instance of 'Meta' "
            f"class '{classname}' from base classes: "
            f"{', '.join(str(base.__name__) for base in bases)}"
        )
        return super().__new__(metacls, classname, bases, namespace)

    def __init__(cls: type, classname: str, bases: tuple[type], namespace: dict[str, Any]) -> None:
        print(f"Initializing class '{classname}'")
        super().__init__(classname, bases, namespace)

    def __call__(cls: type, *args: Any, **kwds: Any) -> type:
        print(f"Calling '__call__' method for class '{cls.__name__}'")
        obj = super().__call__(*args, **kwds)
        print(f"'{obj}' created.")
        return obj


class A(metaclass=Meta):
    """Class 'A' which inherits from 'Meta'."""


a: A = A()

# ─── SECTION 3: DESCRIPTORS ────────────────────────────────────────────────────


T = TypeVar("T")


class TypedDescriptor(Generic[T]):
    """Type descriptor that checks whether an attribute has a correct type."""

    @classmethod
    def verify_type(cls, value: T) -> None:
        if not isinstance(value, cls.expected_type):
            raise TypeError(f"Expected {cls.expected_type}")

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, obj: object | None, objtype: type | None = None) -> T:
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj: object, value: T) -> None:
        self.verify_type(value)
        setattr(obj, self.private_name, value)


class Integer(TypedDescriptor[int]):
    expected_type = int


class Float(TypedDescriptor[float]):
    expected_type = float


class String(TypedDescriptor[str]):
    expected_type = str


class Point:
    x = Integer()
    y = Integer()

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


p: Point = Point(1, 2)

try:
    p.x = "string"
except TypeError as e:
    print(e)


# ─── GENERATORS ───────────────────────────────────────────────────────────────────


def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n
        n -= 1


c: Iterator[int] = countdown(5)
print(next(c))
print(next(c))
print(next(c))

for number in c:
    print(number)