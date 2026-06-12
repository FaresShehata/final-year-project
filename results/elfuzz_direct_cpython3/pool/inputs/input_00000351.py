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
    LOW    = 1 << 32
    NORMAL = 0
    HIGH   = -(1 << 32)


@runtime_checkable
class AsyncIterable(Protocol[K]):
    async def __aiter__(self) -> AsyncIterator[K]:
        ...

    async def __anext__(self) -> K:
        ...


def counter_demo() -> None:
    assert Counter("abcabca") == {"a": 4, "b": 2, "c": 2}
    counter = Counter()
    for i in range(5):
        counter[i] += 1
    print(counter)
    assert counter.most_common() == [(4, 1), (2, 2), (1, 3)]


def counter_demo_2() -> None:
    c = Counter([1, 2, 3, 4])
    d = Counter({"a", "b", "b"})
    e = Counter(a=3, b=-2, c=0)
    f = Counter(("d", "e", "f"))
    g = Counter({int(x): x ** 2 for x in range(3)})
    h = Counter(iter(range(10)))
    assert c["x"] == 0
    assert d.most_common() == [("b", 2), ("a", 1)]
    assert e[None] == 0
    assert len(f) == 2
    assert len(g) == 9
    assert len(h) == 10


def deque_demo() -> None:
    dq = deque((i for i in range(5)), maxlen=5)
    dq.appendleft(6)
    dq.extendleft(dq)
    assert dq == deque((5, 4, 3, 2, 1))
    dq.clear()
    assert dq == deque()


def queue_demo() -> None:
    q = deque((i for i in range(5)), maxlen=5)
    q.appendleft(6)
    q.extendleft(q)
    assert q == deque((5, 4, 3, 2, 1))
    q.clear()
    assert q == deque()


def list_demo() -> None:
    l = [i for i in range(5)]
    assert sorted(l) == [0, 1, 2, 3, 4]
    l.remove(3)
    assert l == [0, 