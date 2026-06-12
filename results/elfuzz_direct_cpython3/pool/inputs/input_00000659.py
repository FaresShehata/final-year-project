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
    NONE         = 0
    SHARED       = 1 << 16
    EXAMPLE      = 1 << 32
    UNICODE      = 1 << 48
    ASCII        = 1 << 64
    DIGIT        = 1 << 78
    ALPHABETIC   = 1 << 98
    ALPHANUMERIC = ALPHABETIC | DIGIT
    CAPS_LOCKED  = ASCI + UNICODE
    NUM_LOCKED   = UNICODE | DIGIT
    ABBREVIATIONS = FLAG.SHARED | 1 << 89
    SYMBOLIC     = DIGIT | ALPHABETIC
    ALL          = (FLAG.ASCII | FLAG.UNICODE | FLAG.DIGIT | FLAG.ALPHABETIC |
                    FLAG.ALBANUMERIC | FLAG.CAPS_LOCKED | FLAG.NUM_LOCKED)
    RICH         = SHARED | UNICODE | ALPHANUMERIC | SYMBOLIC
    EXTENDED     = CAPS_LOCKED | NUM_LOCKED | ABREVIATIONS | SYMBOLIC | ALL



# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Option:
    label: str
    value: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> Option:
        return cls(**d)


@dataclasses.dataclass(frozen=True)
class Character:
    name: str
    priority: int | None = None
    status: Status | None = None
    notes: list[Option] = dataclasses.field(default_factory=list)

    def to_json_safe(self) -> dict[str, object]:
        return {
            "name": self.name,
            "priority": self.priority if self.priority else None,
            "status": self.status.value if self.status else None,
            "notes": [o.to_json_safe() for o in self.notes],
        }


@runtime_checkable
class SearchProtocol(Protocol[K, V]):
    def search(self, key: K) -> V:
        ...


@runtime_checkable
class SortedSearchProtocol(SearchProtocol[K, V]):
    def sort(self, iterable: Iterable[K], reverse=False) -> V:
        ...


@runtime_checkable
class AsyncIterable(Protocol[T]):
    async def __aiter__(self) -> AsyncIterator[T