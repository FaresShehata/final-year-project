"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import inspect
import itertools
import operator
import os
import pathlib
import pickle
import random
import re
import string
import typing as t
import weakref
from collections.abc import (
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Set,
    MutableMapping,
)
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timedelta
from enum import Enum, auto, unique
from enum import (
    IntEnum,
    IntFlag,
    IntDescriptionMixin,
    StrEnum,
    ReprEnum,
    IntFlags,
)
from enum_tools import EnumMeta
from enum_tools.enum_tools import EnumToolsMeta
from enum_tools.repr_enum import ReprEnumMeta
from typing_extensions import Annotated, Self
from unicodedata import lookup
from warnings import warn
import enum
import dataclasses
import enum_tools
try:
    from types import UnionType
except ImportError:
    pass

from .typing_exts import runtime_checkable

# ── Imports ───────────────────────────────────────────────────────────────────

from .misc_utils import get_func_name, make_annotated_typevar, is_async_callable, is_built_in_class, is_coroutine_function, is_dataclass_instance, is_generator_function, is_iterable, is_list_type, is_protocol, is_set_type, is_subclass, is_tuple_type, is_union_type, is_weakref, is_weakref_target
from .misc_utils import is_valid_python_identifier, print_object, print_structured_class, print_type_hint, print_union_type, print_variable

# ── Types ─────────────────────────────────────────────────────────────────────

T_co = t.TypeVar('T_co', covariant=True)
KT = t.TypeVar('KT')
VT = t.TypeVar('VT')

KTT = t.TypeVar("KTT")
VTT = t.TypeVar("VTT")

S = t.TypeVar("S")
T = t.TypeVar("T")

U = t.TypeVar("U")
V = t.TypeVar("V")

W = t.TypeVar("W")

A_co = t.TypeVar("A_co", covariant=True)
B_co = t.TypeVar("B_co", covariant=True)
C_co = t.TypeVar("C_co", covariant=True)


def _make_generic(ty: t.Union[type, t.Any], *args: tuple[t.Any, ...

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


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

