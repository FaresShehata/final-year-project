"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import collections
import enum
import inspect
import json
import logging
import pathlib
import random
import sys
import textwrap
import types
import typing as t
from abc import ABCMeta
from copy import deepcopy
from datetime import timedelta
from functools import partial
from itertools import chain
from math import sin
from typing import Any, Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union

import aioredis
import attrs
import humanize
import more_itertools as mi
import orjson
from attrs import define, field
from attrs.converters import optional
from attrs.validators import instance_of
from attrs_mate import AttrsMateMixin
from hypothesis.strategies import SearchStrategy
from loguru import logger
from more_itertools.more import first_true
from pydantic import BaseModel
from pydantic.generics import GenericModel
from pydantic.types import JSONType
from pydantic.utils import deep_update

from .core import (
    DEFAULT_LOGGING_LEVEL,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_LOGGING_HANDLER,
    DEFAULT_LOGGING_FILE_NAME,
    LogConfig,
    Logger,
    LogLevel,
    LoggingHandler,
    LoggingFormatter,
    LoggingFileBackend,
    LoggingFileHandler,
    setup_logging,
)
from .utils import get_caller_info

# ── Typing aliases ────────────────────────────────────────────────────────────

T = TypeVar("T")
S = TypeVar("S")

if typing.TYPE_CHECKING:

    class Priority(enum.Enum):
        LOW = enum.auto()
        NORMAL = enum.auto()
        HIGH = enum.auto()

    class Status(enum.Enum):
        PENDING = enum.auto()
        RUNNING = enum.auto()
        SUCCESSFUL = enum.auto()
        FAILED = enum.auto()
        CANCELLED = enum.auto()


else:
    Priority = enum.Enum("Priority", ["LOW", "NORMAL", "HIGH"])
    Status = enum.Enum("Status", ["PENDING", "RUNNING", "SUCCESSFUL", "FAILED", "CANCELLED"])

_PRIORITY_ORDER = (Priority.LOW, Priority.NORMAL, Priority.HIGH)


def _validate_priority(value: str):
    for alias in _PRIORITY_ORDER:
        if value.lower().startswith(alias.name.lower()):
            break
    else:
        raise ValueError(f'"{value}" is not a valid priority')


# ── Custom protocols ──────────────────────────────────────────────────────────

@attrs.define(slots=True
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

