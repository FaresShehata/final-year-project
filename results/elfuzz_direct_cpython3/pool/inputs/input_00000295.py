"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import enum
import functools
import inspect
import io
import logging
import os
import pprint
import random
import re
import string
import sys
import timeit
import types
import typing as t
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Callable,
    Collection,
    Container,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from weakref import WeakKeyDictionary

if t.TYPE_CHECKING:
    from types import TracebackType
else:
    from typing import TYPE_CHECKING

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.DEBUG)


def remember(name: str) -> Callable[..., Any]:
    """Decorator for remembering the last value of a function.

    >>> @remember("result")
    ... def square(x: int) -> int:
    ...     return x * x
    ...
    >>> square(42)
    1764
    >>> square.result
    1764
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, name, lambda: getattr(fn, name))
        return fn

    return decorator


# ── Generics ───────────────────────────────────────────────────────────────────

def generic_wrapper(coro: Callable[..., Generator[Any, Any, Any]]) -> Callable[..., Any]:
    @functools.wraps(coro)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        gen = coro(*args, **kwargs)
        try:
            yield next(gen)
        except StopIteration as e:
            return e.value
        else:
            raise RuntimeError(f"{coro} must be an infinite generator")

    return wrapper


@generic_wrapper
def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n
        n -= 1


# ── Decorators ─────────────────────────────────────────────────────────────────

def cached_property(func: Callable[[T], V]) -> property:
    cache = WeakKeyDictionary()

    @property
    def wrapped(inst: T) -> V:
        try:
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

