"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisection
import collections.abc as cabc
import itertools
import math
import os
import platform
import random
import re
import string
import subprocess
import sys
import threading
import time
import types
import typing as t
import weakref

import numpy as np
import pandas as pd
import pytest
import requests as req
import requests_cache as rcc
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from scipy.stats import norm
from sortedcontainers import SortedSet
from toolz.curried import (
    groupby,
    identity,
    partition_all,
)

import py_entitymatching as em
import py_entitymatching.catalog.catalog_utils as cu
import py_entitymatching.base.constants as const
from py_entitymatching.utils.generic_helper import (
    get_unique_str,
    is_empty_list_or_dict,
    is_instance,
    is_iterable,
)
from py_entitymatching.utils.validation_helper import validate_input_args

import pyomnisci as om


if any([sys.version_info >= (3, 9)] +
       [(platform.system() != "Windows" or platform.release() >= "10")]
      ):
    # Python >= 3.9 and MacOS >= 10.15 don't have the bug where 'float('nan')' can be coerced to an integer.
    # We need this check because older versions of PyPy throw exceptions on the line below.
    # This means we cannot use this code for these platforms in our tests.

    class BaseExceptionGroup(Exception):
        """
        A container for multiple exceptions that were raised during execution
        of a single potentially long-running operation.
        """

        def __init__(
                self,
                excs: Union[
                    tuple[BaseException],
                    Iterable[tuple[BaseException]],
                    Sequence[Union[BaseException, Tuple[BaseException]]],
                ],
                message: str | None = None,
                *,
                context: Mapping[str, Any] | None = None,
        ) -> None:

            assert isinstance(excs, (tuple, list))
            assert all(isinstance(x, BaseException) for x in excs)

            if message is None:
                message = f'{len(excs)} exceptions occurred during execution'
            super().__init__(message, *excs)

            self.context = context or {}
            self.exceptions = excs

        def __str__(self) -> str:
            lines = [
                super().__str__()
            ]
            lines.extend(f'{e}\n' for e in self.exceptions)
            return ''.join(lines)


else:
    from collections import UserList

    class BaseExceptionGroup(UserList):
        """
        A container for multiple exceptions that were raised during execution
        of a single potentially long-running operation.
        """

        def __init__(
                self,
                excs: Union[
                    tuple[Exception],
                    Iterable[tuple[Exception]],
                    Sequence[Union[Exception, Tuple[Exception]]],
                ],
                message: str | None = None,
                *,
                context: Mapping[str, Any] | None = None,
        ) -> None:

            assert isinstance(excs, (tuple, list))

            if message is None:
                message = f'{len(excs)} exceptions occurred during execution'
            super().__init__(excs)

            self.context = context or {}
            self.exceptions = excs

        def __str__(self) -> str:
            lines = [
                super().__str__()
            ]
            lines.extend(e.__str__() + '\n' for e in self.exceptions)
            return ''.join(lines)


def raise_if(
        condition: bool,
        msg: str | None = None,
        exc: type[BaseException] = ValueError
) -> None:
    if condition:
        raise exc(msg)


def raise_if_not(
        condition: bool,
        msg: str | None = None,
        exc: type[BaseException]        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, radius: float = 1.0):
