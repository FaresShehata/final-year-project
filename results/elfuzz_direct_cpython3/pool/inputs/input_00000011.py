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
    opcodes = {}
    for i in range(dis.HIGHEST_INSTRUCTION_NUMBER):
        try:
            opcode_name = dis.opname[i]
        except KeyError:
            continue
        else:
            opcodes[opcode_name] = opcodes.setdefault(opcode_name, 0) + 1
    return opcodes


def get_instructions(fn) -> list[tuple[int, str, tuple]]:
    instructions = []
    for i in range(dis.HIGHEST_INSTRUCTION_NUMBER):
        try:
            opcode_name = dis.opname[i]
        except KeyError:
            continue
        instruction_offset = dis.op_offset(i)
        instruction_arg = dis.oparg(i)
        instructions.append((instruction_offset, opcode_name, instruction_arg))
    return instructions


disassembled_python_function = annotated_disassembly(lambda x: x * x)


print("\nPython byte-code disassembled:")
for line in disassembled_python_function.splitlines():
    print(line)

counted_opcodes = count_opcodes(lambda x: x * x)

print("\nCount of each opcode:")
for name, num in counted_opcodes.items():
    print(f"{name}: {num}")

instructions = get_instructions(lambda x: x * x)

print("\nInstructions:")
for offset, opcode_name, arg in instructions:
    print(f"\t{offset}:\t\t{opcode_name}{'' if arg == 0 else ' ' + hex(arg)}")


# ── Disassembly of C functions ─────────────────────────────────────────────────
#
# Note that this wouldn’t be possible on an interpreter because the C library has
# its own virtual machine. In fact, it’s even more interesting than the Python VM
# because it’s written in C.
#
# The Cython project aims to make writing high-performance extensions to Python as
# easy as writing normal Python.

# import ctypes
# import math

# libm = ctypes.CDLL(None)
# libm.sin.restype = ctypes.c_double
# libm.cos.restype = ctypes.c_double
# libm.tan.restype = ctypes.c_double

# def sin(x):
#     return libm.sin(ctypes.c_double(x))


# class MyCFunction(ctypes.Structure):
#     _fields_ = [
#         ("sin", ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)),
#         ("cos", ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)),
#         ("tan", ctypes.CFUNCTYPE(ctypes.c_doublefrom __future__ import annotations

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

