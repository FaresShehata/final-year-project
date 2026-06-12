"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from enum import Enum, IntEnum
from inspect import signature
from random import Random
from types import GenericAlias, ModuleType, TracebackType
from typing import (
    TYPE_CHECKING,
    Any as TAny,
    Callable as TCallable,
    ClassVar,
    Dict,
    ForwardRef,
    List,
    Literal,
    NewType,
    Optional,
    Pattern,
    Sequence,
    Tuple,
    Union,
    cast,
)
from typing_extensions import Annotated, Concatenate, Self, TypeGuard, overload
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from .typing import *

    from .types import *

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

SOME_INT = 42

SOME_FLOAT = 42.42

SOME_STRING = "Hello world!"

SOME_BOOL = True

SOME_LIST = [1, 2, 3, 4, 5]

SOME_TUPLE = (1, 2, 3, 4, 5)

SOME_DICT = {"a": 1, "b": 2}

SOME_SET = {1, 2, 3, 4, 5}

SOME_FROZENSET = frozenset({1, 2, 3, 4, 5})

SOME_RANGE = range(10)

SOME_ITERABLE = SOME_LIST

SOME_ITERATOR = iter(SOME_LIST)

SOME_ASYNC_ITERABLE = SOME_LIST[::2]

SOME_ASYNC_ITERATOR = iter(SOME_LIST[::2])

SOME_GENERATOR = (i for i in range(10))

SOME_ASYNC_GENERATOR = (i for i in range(10)[::2])

SOME_TYPE = type(SOME_LIST)

SOME_NAME = __name__

SOME_MODULE = module()

SOME_CLASS = SomeClass

SOME_FUNCTION = some_function

SOME_PROPERTY = property(lambda *args: args)

SOME_STATIC_METHOD = staticmethod(some_class_method)

SOME_ABSTRACT_CLASS = ABC

SOME_ABSTRACT_METHOD = abstractmethod

SOME_ABC_INSTANCE = SomeABC()

SOME_ABC_SUBCLASS = SubSomeABC()

SOME_ABC_SUPERCLASS = SuperSomeABC()


def some_function(*args, **kwargs) -> None:
    pass


class SomeClass:
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass(eq=True, order=True)
class Student:
    name: str
    age: int
    grades: list[float]

    def average_grade(self) -> float:
        return sum(self.grades) / len(self.grades)


@dataclasses.dataclass(slots=True)
class Person:
    """Class with private attribute."""

    _name: str

    def get_name(self) -> str:
        return self._name.upper() if self._name else ""

    def set_name(self, new_name: str) -> None:
        self._name = new_name[:255]

    def __repr__(self) -> str:
        return f"<Person(name={self.get_name()}, ...>"

    def __str__(self) -> str:
        return f"Name: {self.get_name()}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotObject(object):
    __slots__ = ["_x", "_y"]

    def __init__(self, x: int, y: int) -> None:
        self.set(x, y)

    def set(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return not (self == other)


class NonSlotObject(object):
    __dict__: dict[str, Any]

    def __init__(self, x: int, y: int) -> None:
        self._set(x, y)

    def _set(self, x: int, y: int) -> None:
        self.__dict__["_x"] = x
        self.__dict__["_y"] = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NonSlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, NonSlotObject):
            return NotImplemented
        return not (self == other)


# ─