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
    status: Status = Status.PENDING
    tags: list[str] = []
    metadata: dict = {}
    history: list[Status] = []

    def transition(self, new_status: Status) -> None:
        self.history.append(self.status)
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
            priority=getattr(Priority, data["priority"]),
            status=Status(data["status"]),
            tags=list(data["tags"]),
            metadata=data["metadata"],
        )


# ── Slots & structuring patterns ───────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, order=True, slots=True, unsafe_hash=True)
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * self.width + 2 * self.height


# ── Structured Context Managers ────────────────────────────────────────────────

class Timer(Generic[T]):
    def __init__(self, timeout: T) -> None:
        self.timeout = timeout
        self.started_at = time.monotonic()

    def __enter__(self) -> Timer[T]:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> Literal[False]:

        elapsed_time = time.monotonic() - self.started_at
        if elapsed_time > self.timeout:
            raise TimeoutError(f"Timed out after {elapsed_time:.2f} seconds.")
        return False


# ── Walrus operator ────────────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    return a + b


def multiply(a: int, b: int) -> int:
    return a * b


async def double_async(a: int) -> int:
    return await asyncio.to_thread(add, a, a)


def double_sync(a: int) -> int:
    return add(a, a)


def try_double(a: int) -> int | None:
    try:
        return double_sync(a)
    except TypeError as e:
        print(e)
        return None


async def try_double_async(a: int) -> int | None:
    try:
        return await double_async(a)
    except TypeError as e:
        print(e)
        return None


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    result = try_double_async(1)
    assert result == None
    result = try_double_async(2)
    assert result == None
    result = try_double_async(3)
    assert result == 6


# ── Typing Generics ────────────────────────────────────────────────────────────"""

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


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    fmt = HEADER_FMT.format(magic, version_major, version_minor, len(tag))
    return struct.pack(fmt, *struct.unpack(fmt, tag))


def check_tag(header: bytes, expected_tag: bytes) -> bool:
    magic, _, _, tag_size = struct.unpack(">IHH 4s", header[:HEADER_SIZE])
    return tag_size == len(expected_tag) and tag_size != 0 and tag_size & ~7 == 0 and tag_size >= 3 and header[-tag_size:] == expected_tag


# ── Memory view on buffer ─────────────────────────────────────────────────────

def pickled(buffer: Buffer) -> bytes:
    """Pick a slice of a byte string into a memoryview which will keep it alive."""
    memv = memoryview(buffer)
    pickled_memv = pickle.dumps(memv)
    del memv
    return pickle.loads(pickled_memv)


