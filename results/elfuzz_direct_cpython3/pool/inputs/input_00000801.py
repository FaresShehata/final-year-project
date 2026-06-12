"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc, dataclasses, enum, functools, itertools, math, operator, pathlib, random, re, typing, uuid as _uuid
from collections.abc import Sequence
from functools import singledispatch
from inspect import signature as sig
from numbers import Number
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterator,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
)

import numpy as np
import numpy.typing as npt
import numpy.random as nrnd
import pandas as pd
import PIL.Image as Image
from PIL.PngImagePlugin import PngInfo
from typing_extensions import Concatenate, ParamSpec, Self, TypeGuard, get_args, get_origin, overload

P = ParamSpec("P")
R = TypeVar("R")

V = TypeVar("V", bound=Any)
T = TypeVar("T", bound=Any)


class Enum(enum.Enum):
    pass


class Iterable(Protocol[K]):
    """Iterable protocol."""

    def __iter__(self: Iterable[K]) -> Iterator[K]:
        ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str


@dataclasses.dataclass(frozen=False)
class Planet:
    name: str
    moons: tuple[str, ...]


@dataclasses.dataclass(order=True, frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str


@dataclasses.dataclass(eq=True, order=True, frozen=True)
class Employee(Person):
    department: str
    salary: int


@dataclasses.dataclass(frozen=True)
class Student(Person):
    grade: float


def test_dataclasses() -> None:
    print(max([User(name="Alice", age=25), User(name="Bob", age=30)]))

    # Frozen = True
    user = User(name="Alice", age=25)
    try:
        user.age = 30
    except Exception as e:
        assert type(e) == TypeError

    # Order = True
    person1 = Person(id=1, first_name="John", last_name="Doe")
    person2 = Person(id=2, first_name="Jane", last_name="Smith")
    print(person1 > person2)

    # Eq = True
    employee1 = Employee(
        id=1, first_name="John", last_name="Doe", department="Sales", salary=15000
    )
    employee2 = Employee(
        id=1, first_name="John", last_name="Doe", department="Marketing", salary=18000
    )
    print(employee1 != employee2)

    student1 = Student(id=1, first_name="John", last_name="Doe", grade=90)
    student2 = Student(id=1, first_name="John", last_name="Doe", grade=100)
    print(student1 < student2)

    # Test TypedDict
    class Point(TypedDict):
        x: int
        y: int
        z: int | None

    point = Point(x=1, y=2, z=None)
    print(point["x"], point.get("y"), point.get("z"))


# ── Metaclasses ───────────────────────────────────────────────────────────────

MRO_RECORD = []


class Meta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        MRO_RECORD.append(namespace['__mro__'])
        return super().__new__(cls, name, bases, namespace, **kwargs)

    def __init__(cls, name, bases, namespace, **kwargs):
        MRO_RECORD.append((namespace['__mro__'], cls))
        super().__init__(name, bases, namespace, **kwargs)


class A(metaclass=Meta):

    def method(self):
        pass


class B(A):
    pass