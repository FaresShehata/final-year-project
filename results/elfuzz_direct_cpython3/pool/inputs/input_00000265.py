"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)


if TYPE_CHECKING:
    ...


T = TypeVar("T")
U = TypeVar("U")


def test() -> None:
    assert True


test()


# ── Enums ─────────────────────────────────────────────────────────────────────

# ── Base classes ─────────────────────────────────────────────────────────────-

@dataclasses.dataclass(frozen=True)
class Task:
    """
    A task to be performed.
    """

    id: int
    name: str
    priority: Priority
    status: Status
    tags: List[str]


@enum.unique
class Priority(enum.Enum):
    """Priorities of tasks."""

    NORMAL = 0
    HIGH = 1


@enum.unique
class Status(enum.IntEnum):
    PENDING = 0
    READY = 1
    DONE = 2


@enum.unique
class OperationFailureCode(enum.IntEnum):
    SUCCESS = 0
    FAILED = 1
    CANCELLED = 999


@enum.unique
class OperationResultCode(enum.IntEnum):
    SUCCESS = 0
    FAILED = 1
    CANCELLED = 999


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Serialisable(Generic[T]):
    """A serializable class.

    Attributes:
        id (int): An ID to uniquely identify an instance of the class.
    """

    id: int

    _serialised_attributes: ClassVar[Set[str]] = set()

    def serialise(self) -> dict:
        """Serialises the object into a dictionary."""
        return {attr_name: getattr(self, attr_name) for attr_name in self._serialised_attributes}

    @staticmethod
    def deserialise(serialisation_data: dict) -> T:
        """Deserialises the object from a dictionary."""
        obj = dataclasses.replace(Serialisable(**serialisation_data))
        setattr(obj, "_serialised_attributes", set())
        return obj

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        obj = cls.__new__(cls)
        setattr(obj, "_serialised_attributes", set())
        if not isinstance(value, dict):
            raise TypeError("expected dictionary            "priority": self.priority.name,
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

