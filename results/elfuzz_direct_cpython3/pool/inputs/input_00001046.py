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


fn = lambda x: None


def print_dis(fn):
    print(annotated_disassembly(fn))


print_dis(print_dis)

print_dis(lambda a, b, c: (a + b + c))
print_dis(lambda a, b, *args: (a + b + sum(args)))
print_dis(lambda a, b, **kwargs: (a + b + sum(kwargs.values())))
print_dis(lambda a, b, *, kwarg: a+b+kwarg)
print_dis(lambda a, b, /, kwarg: a + b + kwarg)
print_dis(lambda a, b, /, *, kwarg: a + b + kwarg)
print_dis(lambda a, b, /, kwarg1=None, kwarg2=None, *args, **kwargs: (
    a + b + len(args) + sum(kwargs.values()) + (kwarg1 or 0) + (kwarg2 or 0)))
print_dis(lambda a, b, /, *, kwarg1, kwarg2, *args, **kwargs: (
    a + b + len(args) + sum(kwargs.values()) + (kwarg1 or 0) + (kwarg2 or 0)))


# ── Disasm options ────────────────────────────────────────────────────────────

dis.set_next_line(True)


print_dis(lambda a, b, c: (a + b + c))


def print_dis_annotated(fn):
    print(annotated_disassembly(fn))


def print_dis_with_opts(*opts):
    global fn
    for op in opts:
        setattr(dis, "_OPT_" + op.upper(), getattr(dis.constants, "_" + op.upper()))
    print_dis_annotated(fn)


print_dis_with_opts("NEXT_LINE")

print("\n\n")


# ── Code objects ──────────────────────────────────────────────────────────────

def get_code_object():
    py_func_name = 'get_code_object'
    func = globals()[py_func_name].im_func  # pylint:disable=protected-access
    return func.__code__

func = get_code_object()

print(func.co_argcount)
print(func.co_flags & 16384)  # arg has default value
print(func.co_varnames)
print(func.co_names)
print(func.co_consts)
print(func.co_lnotab.decode('ascii'))
print(func.co_freevars)
print(func.co_cellvars)
print(func.co_firstlineno)
print(func.co_filename)

for i in range(len(func.co_consts)):
    obj = func.co_consts[i]
    if hasattr(obj, "__dict__"):
        obj = obj.__dict__["__wrapped__"]
    print(f"{i}:\n{obj}\n---\n")
    try:
        print(repr(obj))
    except Exception as exc:
        print(exc.args)

try:
    raise Exception([1, 2])
except Exception as e:
    print(e.__traceback__.tb_frame.f_locals)

assert func.co_nlocals <= len(func.co_varnames)
assert func.co_stacksize >= func.co_nlocals
assert func.co_nlocals >= func.co_cellvars.count("_thiscellvar_")
assert func.co_nlocals >= len(func.co_freevars)
assert func.co_stacksize > 0
assert func.co_stacksize <= sys.maxsize
assert func.co_stacksize % 2 == 0


# ── Ctypes ───────────────────────────────────────────────────────────────────    def is_terminal(self) -> bool:
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


class PriorityQueue(Generic[K, V]):
    """
