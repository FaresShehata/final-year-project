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

# ── Descriptors ────────────────────────────────────────────────────────────────


class _BoolDescriptor(object):
    """
    This descriptor is used to demonstrate how an object can be defined with a
    custom get/set method that returns and sets boolean values.
    """

    def __init__(self, name: str):
        self.name = f"_{name}"

    def __get__(self, instance: Optional[_BoolDescriptor], owner: type) -> bool:
        return getattr(instance, self.name)

    def __set__(self, instance: Optional[_BoolDescriptor], value: bool) -> None:
        setattr(instance, self.name, value)


class Foo(_BoolDescriptor):
    pass


class Bar(_BoolDescriptor):
    pass


# ── Classes for the test suite ─────────────────────────────────────────────────


class ContextManager:
    """A simple class that implements `with` statements."""

    def __enter__(self) -> ContextManager:
        print(f"{type(self)} enter")
        return self

    def __exit__(self, *args: Any) -> None:
        print(f"{type(self)} exit")


class BaseClass:
    """A simple class with some attributes."""

    foo: bool
    bar: bool
    baz: bool

    def __init__(
        self,
        *,
        foo: bool = False,
        bar: bool = True,
        baz: bool = False,
    ) -> None:
        self.foo = foo
        self.bar = bar
        self.baz = baz

    def do_stuff(self) -> None:
        ...


class DerivedClass(BaseClass):
    """A derived class of :py:class:`BaseClass`. It overrides most methods."""

    foo: bool
    bar: bool
    baz: bool

    def __init__(
        self,
        *,
        foo: bool = False,
        bar: bool = True,
        baz: bool = False,
    ) -> None:
        super().__init__(foo=foo, bar=bar, baz=baz)
        self.foo = not foo
        self.bar = not bar
        self.baz = not baz

    def do_stuff(self) -> None:
        ...

    def custom_method(self) -> None:
        ...


class PseudoEnum(int, enum.IntFlag):
    A = 1 << 0
    B = 1 << 1
    C = 1 << 2


class EnumWithMethods(enum.Flag):
    A = 1 << 0
    B = 1 << 1import typing
import weakref

import numpy as np
import numpy.typing as npt

try:
    import tracemalloc
except ImportError:
    tracemalloc = False

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple, TypeVar
    from collections.abc import Sequence, MutableMapping, Mapping
else:

    def make_adder_from_bytecode(delta: int) -> types.FunctionType:
        pass


class Mode(enum.Enum):
    default = enum.auto()
    debug = enum.auto()


_MODE = Mode.default
_TIME_FUNCTION = bool(os.environ.get("TIME_FUNCTION", False))
del os, enum


# ── High-level functions ──────────────────────────────────────────────────────

LARGE_INTS = [
    9_567_983_233_547_022_263,
    -9_567_983_233_547_022_263,
]
LARGE_FLOATS = [
    9_567_983_233_547_022_263.432,
    -9_567_983_233_547_022_263.432,
]


def sum_odd_squares(
    start: int = LARGE_INTS[0],
    stop: int = LARGE_INTS[-1],
    delta: int = 2,
) -> int:
