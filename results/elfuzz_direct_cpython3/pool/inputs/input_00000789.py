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

# ── Classes and Interfaces ───────────────────────────────────────────────────


@runtime_checkable
class HasStatus(Protocol[K]):
    status: Status

@dataclasses.dataclass(order=True, frozen=True)
class Completed(K):     # K is HasStatus
    value: V
    timestamp: float = dataclasses.field(default_factory=time.time)
    status: Status = Status.SUCCESS

@dataclasses.dataclass(order=False, frozen=True)
class Pending(K):       # K has no order
    created_at: float = dataclasses.field(default_factory=time.time)
    status: Status = Status.PENDING


@dataclasses.dataclass(order=True, frozen=True)
class Running(Pending[V]):      # K has no order
    result: T | None             # K is has_order as well as has_status
    progress: float              # how much done? 0 <= x < 1

@dataclasses.dataclass(order=True, frozen=True)
class Failed(Running[V]):       # K has no order
    exn: BaseException


class Queue(Generic[K], list[K]):

    def append(self, obj: K) -> None:
        bisect.insort(self, obj)

    @overload
    def pop_first(self) -> K: ...
    @overload
    def pop_first(self, default: K) -> K | None: ...

    def pop_first(self, default: K | None = None) -> K | None:
        try:
            return self.pop(0)
        except IndexError:
            return default


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class DataClass:
    ID: int
    Name: str
    Age: int


# ── Structs ───────────────────────────────────────────────────────────────────

struct_struct = struct.Struct("<i")


def read_from_file(path: str) -> None:
    with open(path, 'rb') as fd:
        while True:
            data = fd.read(4)
            if not data:
                break
            age = struct.unpack(struct_struct, data)[0]
            print(age)


def write_to_file() -> None:
    buf = bytearray()
    for i in range(5):
        buf.extend(struct_pack('<i', i))
    with open('numbers.bin', 'wb') as fd:
        fd.write(buf)


def main():
    print('Data class')
    d = DataClass(ID=1, Name='Alice', Age=29)
    print(d.ID)
    print(d.Name)
    print(d.Age)
    print
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
    co_new = co.replace(co_name=new_name)
    fn_new = types.FunctionType(
        co_new,
        globals(),
        name=new_name,
        argcount=len(co.co_varnames),
        nlocals=len(co.co_cellvars),
        stacksize=co.co_stacksize,
        flags=co.co_flags,
        lnotab=co.co_lnotab.copy(),
        consts=list(co.co_consts),
        names=co.co_names,
        varnames=co.co_varnames,
        filename=co.co_filename,
        name=None,           # remove the original name from the cloned function
        freevars=tuple(),    # cloning does not create any free variables
        cellvars=co.co_cellvars,
    )
    setattr(fn_new, "__module__", fn.__module__)
    return fn_new


def clone_code_object(fn: types.FunctionType | None = None) -> tuple[types.CodeType, types.FunctionType]:
    """Clone the code object and add a new name to it."""
    co = getattr(fn or hot_path, '__code__', None)
    assert isinstance(co, types.CodeType)
    # The following line is equivalent to the two above lines.
    # co = co.clone(name='clone')       # not working on Python 3.7...
    # co = types.CodeType(*co.co_code, co.co_kwonlyargcount, co.co_nlocals, ...)
    co_new = co.replace(
        co_name="clone",
        filename=__file__,
    )
    fn_new = types.FunctionType(
        co_new,
        globals(),
        name="clone",
        argcount=len(co.co_varnames),
        nlocals=len(co.co_cellvars),
        stacksize=co.co_stacksize,
        flags=co.co_flags,
        lnotab=co.co_lnotab.copy(),
        consts=list(co.co_consts),
        names=co.co_names,
        varnames=co.co_varnames,
        filename=co.co_filename,
        name=None,           # remove the original name from the cloned function
        freevars=tuple(),    # cloning does not create any free variables
        cellvars=co.co_cellvars,
    )
    setattr(fn_new, "__module__", fn.__module__)   # pass original module back
    return (co_new, fn_new)


# ── CTypes ────────────────────────────────────────────────────────────────────

def c_short(value: int) -> ctypes.c_short:
    return ctypes.c_short(int(math.fabs(value)))


def c_int_8bit(value: int) -> ctypes.c_byte:
    return ctypes.c_byte(value)


def c_uint_8bit(value: int) -> ctypes.c_ubyte:
    return ctypes.c_ubyte(value)



# ── Struct ────────────────────────────────────────────────────────────────────

def pack_float(f: float) -> bytes:
    fmt = "f"
    size = struct.calcsize(fmt)
    raw_bytes = struct.pack(fmt, f)
    return raw_bytes[:size]


def unpack_float(raw: bytes) -> float:
    fmt = "f"
