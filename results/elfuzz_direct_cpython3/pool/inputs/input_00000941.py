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
import typing
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from enum import Enum as PythonEnum
from enum import auto
from functools import partialmethod
from inspect import signature
from numbers import Number
from os.path import join
from pathlib import Path
from pprint import pformat, pprint
from re import match
from timeit import default_timer as timer
from types import MethodType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
    runtime_checkable,
)
from warnings import warn

if typing.TYPE_CHECKING:
    from collections.abc import Collection
else:
    Collection = object()

from more_itertools import unique_everseen

import attr
import enum
import jsonschema
import marshmallow.fields
import numpy as np
import pandas as pd
import pluggy
import pydantic_core
from hypothesis.strategies import complex_numbers, integers
from hypothesis.strategies.composite import composite
from hypothesis.strategies.generic_sets import SetStrategy
from hypothesis.strategies.integers import ints
from hypothesis.strategies.lists import lists
from hypothesis.strategies.tuples import tuples
from hypothesis.strategies.xml_elements import xml_element
from hypothesis_verify import verify
from hypothesis_verify.results import NotAccepted
from hypothesis_verify.verify import check
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pytest import mark
from strictyaml import YAML, load
from typing_extensions import Literal, Protocol, TypedDict, final

from seed00.shared.constants import SEED_PREFIX


# seed01
# -------
# The following snippets were written by me (Hannah Reimann), with some inspiration from
# other sources. Feel free to use them for your projects!


def get_seed_prefix():
    prefixes = [f"seed{str(i).zfill(6)}" for i in range(1, 7)]
    prefix = SEED_PREFIX
    assert prefix is None or prefix.strip() == ""
    if prefix is None:
        return prefixes[0]

    for seed_prefix in prefixes:
        if seed_prefix.startswith(prefix):
            return seed_prefix
    else:
        return prefixes[-1]


class Animal(Enum):
    CAT = "cat"
    DOG = "dog"


@attr.s(auto_attribs=True, frozen=True)
class AnimalData:
    name: str
    species: str
   
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value!r} must be of type {self.expected_type}")
        if self.lo is not None and value < self.lo or self.hi is not None and value > self.hi:
            raise ValueError(
                f"value {value!r} must be in the range [{self.lo}, {self.hi}]"
            )
        setattr(obj, self.name, value)


def int_range(lo=None, hi=None):
    """
    Create a descriptor enforcing an integer range.

    Arguments are passed to ``TypedDescriptor``.
    """

    class IntRange(TypedDescriptor):
        expected_type = int

    return IntRange(lo=lo, hi=hi)


T_co = TypeVar("T_co", covariant=True)
S = TypeVar("S")


class StringEnum(str, enum.Enum):
    pass


class StrEnum(StringEnum):
    def __new__(cls, *values: Any, **kwargs: Any) -> "StrEnum":
        obj = super().__new__(cls, values[0])
        obj._value_ = values[0]
        for v in values[1:]:
            if v != cls(v)._value_:
                raise ValueError(f"All choices must have the same string value")
        obj.value = values[0]
        return obj


@dataclass(unsafe_hash=True)
class Point2D:
    x: float
    y: float


Point3D = dataclasses.make_dataclass(
    "Point3D",
    ["x", "y", "z"],
    namespace={"__post_init__": lambda self: print(self)},
)


class SingletonMeta(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:

        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwds)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """A singleton example."""

    def hello(self):
        print("Hello")


class DuckType:
    def quack(self):
        ...


class ConcreteDuck(DuckType):
    def fly(self):
        ...


def main() -> None:
    """"""

    # 1. Methods: Abstract Base Classes
    print()
    print("-" * len("Methods: Abstract Base Classes"))
   