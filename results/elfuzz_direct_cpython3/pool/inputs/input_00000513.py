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


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)


def rename_module(mod: types.ModuleType, old_name: str, new_name: str) -> None:
    """Change mod.__name__ and mod.__file__ if necessary.
    This is useful when you want to monkeypatch modules without changing their
    original contents.
    """
    mod.__name__ = new_name
    mod.__spec__.name = new_name


def patch_importer(path: str, loader: importlib.abc.Loader) -> None:
    """Use another Loader subclass to load files at path."""
    sys.path_importer_cache[path] = loader


def patch_submodule(module: types.ModuleType, submodule: str | bytes) -> None:
    """Create a new submodule with the same attributes as module.submodule."""
    spec = importlib.util.find_spec(submodule, package=module.__name__)
    assert spec
    setattr(module, submodule, importlib.util.module_from_spec(spec))


# ── Ctypes ────────────────────────────────────────────────────────────────────

def carray(n: int, dtype: type[float | int]) -> array.array[float | int]:
    """Return an array whose items are initialized by pointing to a memory block
    allocated with ctypes.c_array(). The caller must ensure that the array size
    does not exceed the number of elements specified by the ctypes size parameter.
    """
    return array.array(dtype, (ctypes.c_float() for _ in range(n)))


# ── Struct ────────────────────────────────────────────────────────────────────

def pack(fmt: str, /, *args) -> bytearray:
    """Pack multiple values according to fmt into a buffer and return the results
    as a bytes-like object.

    Supported formats:
      * c — signed char
      * b — signed char
      * h — short
      * H — unsigned short
      * i — int
      * I — unsigned int
      * l — long
      * L — unsigned long
      * q — long long
      * Q — unsigned long long
      * N — size_t
      * f — float
      * d — double
    """
    return struct.pack(fmt, *args)


def unpack(
    fmt: str | bytes, /, byte_string: bytes | bytearray, /, *, sizes=None
) -> tuple[Any]:
    """Unpack values from packed data according to fmt and return them as a tuple.

    Supported formats:
      * c — signed char
      * b — signed char
      * h — short
      * H — unsigned short
      * i — int
      * I — unsigned int
      * l — longimport functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

VARS = [
    ZERO,
    ONE,
    TWO,
    THREE,
    FALSE,
    TRUE,
    AND,
    OR,
    NOT,
    ADD,
    MUL,
    SUCC,
]


def show_eval(expr: Any, vars: list[Any]) -> any:
    """
    >>> show_eval(TRUE(), VARS)
    True

    >>> show_eval(IF(TRUE()), VARS)
    3
    """

    for v in vars:
        if expr == v:
            return v
    else:
        return IF(show_eval(expr[0], vars))(show_eval(expr[1], vars))(
            show_eval(expr[2], vars)
        )


# ── Higher-order functions, map/filter/reduce/reduce-left/accumulate/map-acc/… ──

F = Callable[[Any], Any]


def map_acc(f: F, iterable: Iterable[A], initial: B = None) -> list[B]:
    """
    >>> map_acc(lambda a: a * 2, [0, 1, 2])
    [0, 2, 4]

    >>> map_acc(lambda a: a * 2, [0, 1, 2], 1)
    [1, 2, 4]
    """
    result: list[B] = []
    total = initial or 0
    for i, e in enumerate(iterable):
        result.append(total := total + f(e))
    return result


def filter_acc(predicate: F, iterable: Iterable[A], default: A | None = None) -> list[A]:
    """
    >>> filter_acc(lambda a: a > 10, [0, 1, 2, 3, 4])
    [11, 12, 13, 14]

    >>> filter_acc(lambda a: a > 10, [0, 1, 2, 3, 4], 100)
    [100, 101, 102, 103, 104]
    """
    result: list[A] = []
    for e in iterable:
        if predicate(e):
            result.append(e)
        else:
            result.append(default)
    return result


def reduce_acc(
    func: Callable[[B, A], B], iterable: Iterable[A], initval: B = None
) -> B:
    """
    >>> reduce_acc(operator.add,
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


