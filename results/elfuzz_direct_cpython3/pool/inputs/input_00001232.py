"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import typing as t
import unittest
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from functools import partial, wraps
from hashlib import sha1
from itertools import count
from numbers import Number
from operator import attrgetter
from os.path import basename, dirname, join
from pathlib import Path
from platform import python_version_tuple
from queue import Queue
from re import match
from timeit import timeit
from types import CodeType, FunctionType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Mapping,
    NoReturn,
    NewType,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from uuid import UUID
from weakref import WeakKeyDictionary

try:
    from typing_extensions import Self
except ImportError:
    from typing import Self

# ── Name mangling ───────────────────────────────────────────────────────────-

print("\nName mangling")

# The mangled names should look like this:

# * Functions, methods, classes: `<module>.__<function/method/class>_name`
# * Attributes: `<object>.<attribute>`
# * Module globals: `<module>.<global>`


# ── Constants ────────────────────────────────────────────────────────────────

CONSTANT_A: int = 123456789
CONSTANT_B: float = -123456789.123456789
CONSTANT_C: str = "Hello World"
CONSTANT_D: tuple[int, bool] = (1, True)
CONSTANT_E: set[float] = {1.23}
CONSTANT_F: frozenset[complex] = frozenset({1+2j, 3-4j})
CONSTANT_G: tuple[bool, ...] = (True,)
CONSTANT_H: tuple[None, ...] = (None,)
CONSTANT_I: tuple[str, ...] = ("",)

# ── Literals ─────────────────────────────────────────────────────────────────

LITERAL_A: Literal["a"] = "a"
LITERAL_B: Literal[-1] = -    def __set_name__(self, owner: type, name: str) -> None:
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


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
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

class CachingDecorator(CachedProperty):<|cursor|>
