"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import functools
import inspect
import random
import time
from collections.abc import Callable, Iterator, Iterable, Sized, Mapping, Sequence
from contextlib import suppress
from datetime import timedelta
from enum import Enum
from types import GenericAlias
from typing import (
    Any,
    Literal,
    overload,
    TypeVar,
    Protocol,
    runtime_checkable,
    Union,
    AsyncIterator,
    Final,
    ClassVar,
    FinalVar,
    NoReturn,
    ParamSpec,
    TypeGuard,
)


# ─── Helper Functions ───────────────────────────────────────────────────────────

def _try_to_int(arg: Any) -> int | None:
    try:
        return int(arg)
    except (ValueError, TypeError): pass

    return None


def _try_to_float(arg: Any) -> float | None:
    try:
        return float(arg)
    except (ValueError, TypeError): pass

    return None


def _try_to_bool(arg: Any) -> bool | None:
    try:
        return bool(arg)
    except (ValueError, TypeError): pass

    return None


def _try_to_str(arg: Any) -> str | None:
    try:
        return str(arg)
    except (ValueError, TypeError): pass

    return None


def _try_to_list(arg: Any) -> list[Any]:
    try:
        return list(arg)
    except (ValueError, TypeError): pass

    return []


def _try_to_tuple(arg: Any) -> tuple[Any]:
    try:
        return tuple(arg)
    except (ValueError, TypeError): pass

    return ()

def _check_sequence(seq: Any) -> bool:
    """
    Check if the argument is a sequence.

    Args:
        seq: The argument to be checked.

    Returns:
        A boolean indicating whether the argument is a sequence.
    """

    if isinstance(seq, (list, set)):
        return True
    
    elif callable(getattr(seq, "__iter__", None)) == lambda: True:
        return True
    
    else:
        return False


# ─── Awaitables & Promises ─────────────────────────────────────────────────────

async def sleep() -> None:
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    while True:
        await asyncio.sleep(random.uniform(1, 5))
        print(time.perf_counter())


# ─── Coroutines ───────────────────────────────────────────────────────────────

async def add(x: int, y: int) -> int:
    return x + y

async def multiply(x: int, y: int) -> int:
    return x * y

async def subtract(x: int, y: int) -> int:
    return x - y


# ─── Protocols ────────────────────────────────────────────────────────────────

class Item(object):

    id: int = 1

    @classmethod
    def generate_id(cls) -> int:
        return cls.id

    def get_title(self) -> str:
        raise NotImplementedError()


class Book(Item):

    title: str = ""
    author: str = ""


class Person:

    first_name: str = ""
    last_name: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Customer(Person):

    cart: list[Book]


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclasses.dataclass
class TodoItem:
    task: str
    completed: bool = False


@dataclasses.dataclass(order=True)
class PriorityTodoItem(TodoItem):
    priority: int = 1


@dataclasses.dataclass
class NestedDataClass:
    book: Book
    person: Person


# ─── Slots ────────────────────────────────────────────────────────────────────

# NOPEP8: disable for slots
@dataclasses.dataclass(slots=True)
class SlotClass:
    """A class# ── Descriptors ──────────────────────────────────────────────────────────────

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

