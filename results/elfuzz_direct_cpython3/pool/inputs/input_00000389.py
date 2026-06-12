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

# ── dis - decodes bytecodes from a .pyc or .pyo file ──────────────────────────

PYTHON_BYTECODES = {
    'dis': dis.dis,
    'load_const': load_const,
    'load_name': load_name,
    'build_class': build_class,
}

for name, fn in PYTHON_BYTECODES.items():
    print(f"Disassembling {name}:")
    print(annotated_disassembly(fn))
    print()


# ── Code Objects ──────────────────────────────────────────────────────────────

SOURCE_CODE = textwrap.dedent("""
    def foo(x):
        x += 1
    del x
    """).strip()
print("\nCode object:")
CO = compile(SOURCE_CODE, filename="<demo>", mode="exec")

print(CO.co_filename)
print(CO.co_firstlineno)
print(CO.co_consts)
print(CO.co_names)
print(CO.co_varnames)

if CO.co_argcount == 0:
    print("No positional arguments.")
elif CO.co_argcount == 1:
    print("One positional argument:", CO.co_varnames[0])
else:
    raise Exception("Unexpected number of parameters.")

print(CO.co_kwonlyargcount)
print(CO.co_flags)

# ── Struct ───────────────────────────────────────────────────────────────────

CUSTOM_STRUCT_FORMAT = "<iIff"

# This is the size of the structure: i = 4 bytes, I = 8 bytes, f = 4 bytes.
SIZE = struct.calcsize(CUSTOM_STRUCT_FORMAT)

s = struct.pack(CUSTOM_STRUCT_FORMAT, 0x7f, 0xffff_ffff, 3.14, 4.2)

print(struct.unpack_from(CUSTOM_STRUCT_FORMAT, s)[0])

# You can use struct.pack_into() to write into an existing buffer.

# The second argument must be an addressable object that implements the buffer API.


CUSTOM_STRUCT_FORMAT = "<iIiff"
# This is the size of the structure: i = 4 bytes, I = 8 bytes, f = 4 bytes.
SIZE = struct.calcsize(CUSTOM_STRUCT_FORMAT)

b = bytearray(b"\xff\xff\xff\xff\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00")

struct.pack_into(CUSTOM_STRUCT_FORMAT, b, 0, 0x7f, 0xffff_ffff, 3.14, 4.2)

print(struct.unpack_from(CUSTOM_STRUCT_FORMAT, b)[0])


# ── Array ────────────────────────────────────────────────────────────────────

# An array holds values of only one type.

ARRAY_TYPE = array.array

a = ARRAY_TYPE([1, 2, 3])  # Type hinted as array.array[int].
a = ARRAY_TYPE('d', [1., 2., 3.])  # Type hinted as array.array[float].

# A multidimensional array is possible:

A = ARRAY_TYPE('dd')
B = ARRAY_TYPE('dd')

AB = A.frombytes(B.tobytes())

# ── MemoryView ───────────────────────────────────────────────────────────────

MVIEW = memoryview

MEMVIEW = MVIEW(bytearray(b'\x00' * 6))


# ── Pickle ───────────────────────────────────────────────────────────────────

PICKLEABLE_TYPES = (
    bool,
    bytes,
    complex,
    float,
    int,
    str,
    tuple,
    type(None),
    frozenset,
    set,
    slice,
    type,
    collections.namedtuple,
    functools.partial,
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
            del self._data[idx]

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(something: str | int) -> str:
    match something:
        case str():
            return f"string: {something!r}"
        case int():
