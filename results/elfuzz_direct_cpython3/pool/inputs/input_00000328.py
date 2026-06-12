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
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
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
class Serializable(Protocol[K, V]):
    """
    A protocol defining the interface for serialisation. The `to_json` method must be implemented.
    """

    def to_json(self) -> str:
        ...


def serialise(obj: Serializable) -> str:
    return obj.to_json()


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Task(Serializable[int, str, Priority, Status, list[str]]):  # type: ignore[valid-type]
    """
    Simple task model with a few fields.

    This class satisfies both the `Serializable` protocol and the JSONable protocol.
    It also implements dataclasses.eq, dataclasses.hash, and dataclasses.frozen.
    """

    id: int
    name: str
    priority: Priority
    status: Status
    tags: list[str]

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @property
    def done(self) -> bool:
        return self.status.is_terminal()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            raise TypeError(f"'==' not supported between '{type(self)}' and '{type(other)}'")
        return all(getattr(self, field) == getattr(other, field) for field in self.__dataclass_fields__.keys())

    def __hash__(self) -> int:
        return hash(tuple(sorted((getattr(self, field) for field in self.__dataclass_fields__.keys()))))

    def __str__(self) -> str:
        return f"{self.name} - {self.status}"

    def __repr__(self) -> str:
        return f"<{self.__module__}.{self.__class__.__qualname__}(id={self.id}, name='{self.name}')>"

    @overload
    @staticmethod
    def from_id(id_: K) -> Task[K, V]: ...

    @overload
    @staticmethod
    def from_name(name: str) -> Task[K, V]: ...

    @overload
    @staticmethod
    def from_priority(priority: Priority) -> Task[K, V]: ...

    @overload
    @staticmethod
    def from_status(status: Status) -> Task[K, V]: ...

    @classmethod
    def from_id(cls, id_: int) -> Task:
        return cls(
            id=id_,
            name=f"id-{id            "id": self.id,
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

