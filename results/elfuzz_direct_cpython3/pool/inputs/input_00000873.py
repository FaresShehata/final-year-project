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

print("Bytecode disassemblies")
assert annotated_disassembly(hot_path) == """
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with inspection")
assert annotated_disassembly(inspect.getsource(hot_path)) == """
  3           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               0 (2)
              4 COMPARE_OP               6 (<)
              8 POP_JUMP_IF_FALSE       19
             10 LOAD_FAST                0 (n)
             12 LOAD_FAST                0 (n)
             14 BINARY_MULTIPLY
             16 STORE_FAST               1 (total)
             18 JUMP_ABSOLUTE            5
             21 LOAD_FAST                1 (total)
             23 LOAD_FAST                0 (n)
             25 BUILD_SLICE              1
             27 BINARY_SUBTRACT
             29 STORE_FAST               1 (total)
             31 JUMP_ABSOLUTE            5
             34 LOAD_CONST               1 (None)
             36 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_FALSE': 1, 'BINARY_MULTIPLY': 1, 'STORE_FAST': 2, 'JUMP_ABSOLUTE': 2, 'BUILD_SLICE': 1, 'BINARY_SUBTRACT': 2, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with dis.symtable")
assert annotated_disassembly(dis.symtable(hot_path)) == """
Disassembling hot_path:
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""


# ─────── Code Objects ─────────────────────────────────────────────────────────

def test_code_object() -> None:

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__
    assert co.co_argcount == 1, "co.argcount is incorrect"
    assert len(co.co_varnames) == 4, "co.varnames are not correct"
    assert co.co_freevars == ("x", "y", "z"), "co.freevar names are not correct"
    assert co.co_cellvars == (), "co.cellvars are not empty"
    assert co.co_name == "foo", "co.name is incorrect"

    print(repr(co))
    print(f"co.names are {co.co_names}")
    assert "x" in co.co_names and "y" in co.co_names and "z" in co.co_names, \
        "not all identifiers used as arguments were included in co.names"
    assert len(set(co.co_names)) == len(co.co_names), \
        "there are duplicate entries in co.names"
    print(f"co.lnotab is {co.co_lnotab}")

    assert co.co_filename.endswith("/test.py"), f"{co.co_filename} does not match expected filename"

    print(f"co.starts line {co.co_firstlineno}, ends on line {co.co_endline}")


# ──────────────────────────────────────────────────────────────────────────────

def test_code_objects() -> None:
    print("\nCode objects")

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__

    print(f"name of function: {co.co_name!r}")
    print(f"type of function: {type(foo)}")
    print(f"function starts on line {co.co_firstlineno}")
    print(f"function ends on line {co.co_endline}")

    print(f"number of args: {co.co_argcount}")
    print(f"variable names: {list(co.co_varnames)!r}")
    print(f"free variables: {list(co.co_freevars)!r}")
    print(f"cell variables: {list(co.co_cellvars)!r}")
    print(f"filename: {co.co_filename!r}")
    print(f"path of file containing function: {co.co_sourcefile!r}")
    print(f"line numbers where function is called: {co.co_lnotab!r}")

    print(f"is a closure: {bool(co.co_flags & CO_GENERATOR)}")
    print(f"return type annotation: {co.co_returnannotation!r}")
    print(f"global names: {list(co.co_globalnames)!r

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

    def extend(self, items: Iterable[T]) -> None:
        for item in items:
            bisect.insort(self._data, item)  # type: ignore[arg-type]

    def remove(self, item: T) -> None:
        i = self._data.index(item)  # type: ignore[arg-type]
        del self._data[i]

    def index(self, item: T) -> int:
        return self._data.index(item)  # type: ignore[arg-type]


class MinHeap(SortedList[int]):
    """Same as a regular heap but with the minimum value always at head."""

    def __init__(self) -> None:
