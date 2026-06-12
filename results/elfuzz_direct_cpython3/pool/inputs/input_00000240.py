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
from collections.abc import Callable, Generator, Iterable, Iterator, Reversible
from enum import Enum, unique
from typing import Any, TypeVar, cast, overload
from uuid import UUID, uuid4

import attr
import attrs
import attr.validators as validators
import dataclasses
import enum
import inspect
import os
import pickle
import re
import textwrap
import types
import warnings
from contextvars import ContextVar
from enum import auto, Enum
from functools import cache, cached_property, lru_cache
from ipaddress import IPv4Address
from pathlib import Path
from random import Random
from string import ascii_uppercase, digits
from time import sleep
from typing import (
    TYPE_CHECKING,
    Awaitable,
    ClassVar,
    Deque,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeAlias,
    TypedDict,
    Union,
)
from urllib.parse import ParseResult, parse_qsl, urlencode, urlsplit, urlunparse
from weakref import WeakKeyDictionary

from sanic.log import logger
from sanic.response import HTTPResponse
from sanic.views import HTTPMethodView

if TYPE_CHECKING:
    from collections.abc import Mapping


class BaseEnum(Enum):
    """Base class for all enums.

    Provides a context manager that sets the current enum value on enter.
    """

    def __enter__(self) -> Enum:
        old_enum_value = cast(Optional[int], getattr(sys, "__enum_values"))
        setattr(sys, "__enum_values", {**sys.__enum_values, self.name: self.value})
        return self

    def __exit__(self, *exc_info: Any) -> None:
        setattr(sys, "__enum_values", old_enum_value)


@unique
class Priority(BaseEnum):
    LOW = auto()
    NORMAL = auto()  # default
    HIGH = auto()


class AccountType(enum.Enum):
    PERSONAL = "personal"
    BUSINESS = "business"

    @property
    def is_personal(self) -> bool:
        return self == AccountType.PERSONAL

    @property
    def is_business(self) -> bool:
        return not self.is_personal


def identity(x: Any) -> Any:
    return x


def validate_id(value: Any) -> None:
    try:
        UUID(str(value))
    except ValueError:
        raise ValueError("Invalid ID")


# ── Des    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

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

