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
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Disassembling the standard library ────────────────────────────────────────


def dump_stdlib():
    """Show some examples of how to use dis."""
    import binascii
    import functools
    import hashlib
    import hmac
    import json
    import math
    import os
    import random
    import secrets
    import shutil
    import string
    import timeit

    print("-" * 80)
    print(f"{binascii.binascii.__name__:>36} bytecode:")
    print(annotated_disassembly(binascii.binascii))
    print()

    print("-" * 80)
    print(f"{functools.lru_cache.__name__:>36} bytecode:")
    print(annotated_disassembly(functools.lru_cache))
    print()

    print("-" * 80)
    print(f"{hashlib.sha256.__name__:>36} bytecode:")
    print(annotated_disassembly(hashlib.sha256))
    print()

    print("-" * 80)
    print(f"{hmac.compare_digest.__name__:>36} bytecode:")
    print(annotated_disassembly(hmac.compare_digest))
    print()

    print("-" * 80)
    print(f"{json.dumps.__name__:>36} bytecode:")
    print(annotated_disassembly(json.dumps))
    print()

    print("-" * 80)
    print(f"{math.isclose.__name__:>36} bytecode:")
    print(annotated_disassembly(math.isclose))
    print()

    print("-" * 80)
    print(f"{os.kill.__name__:>36} bytecode:")
    print(annotated_disassembly(os.kill))
    print()

    print("-" * 80)
    print(f"{random.shuffle.__name__:>36} bytecode:")
    print(annotated_disassembly(random.shuffle))
    print()

    print("-" * 80)
    print(f"{secrets.token_bytes.__name__:>36} bytecode:")
    print(annotated_disassembly(secrets.token_bytes))
    print()

    print("-" * 80)
    print(f"{timeit.repeat.__name__:>36} bytecode:")
    print(annotated_disassembly(timeit.repeat))
    print()

    print("-" * 80)
    print(f"{shutil.copyfileobj.__name__:>3    def from_dict(cls, data: dict) -> "Serialisable": ...


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

