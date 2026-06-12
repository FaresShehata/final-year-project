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
    """Inspect the calling frame.

    Returns dictionary with keys 'caller', 'called' and 'callers_caller'.
    """
    callers_frame = sys._getframe(depth)
    called_frame = callers_frame.f_back
    caller_frame = called_frame.f_back
    return {
        "caller": caller_frame.f_code.co_name,
        "called": called_frame.f_code.co_name,
        "callers_caller": callers_frame.f_back.f_code.co_name,
    }


def get_arg_spec(fn: Callable[..., Any]) -> inspect.FullArgSpec:
    return inspect.getfullargspec(fn)


# ── Garbage collection ────────────────────────────────────────────────────────

def mark_all_garbage() -> None:
    gc.collect()


def collect_all_references() -> Set[Any]:
    refs: set = set()
    gc.get_referrers(refs)
    return refs


# ── Memory allocation statistics ───────────────────────────────────────────────

def memory_usage() -> tuple[int, int]:
    return resource.getrusage(resource.RUSAGE_SELF)[2], resource.getrusage(resource.RUSAGE_SELF)[4]


# ── Type hinting ──────────────────────────────────────────────────────────────

def my_sum(numbers: Iterable[float]) -> float:
    sum_ = 0.0
    for number in numbers:
        sum_ += number
    return sum_


def my_sum_generic(numbers: Sequence[float]) -> float:
    sum_ = 0.0
    for number in numbers:
        sum_ += number
    return sum_


# ── Pickling and unpickling ───────────────────────────────────────────────────

class ColoredPoint(Point):
    color: str


def pick_state(point: Point) -> bytes:
    return pickle.dumps({"x": point.x, "y": point.y})


def unpick_point(packed_data: bytes) -> Point:
    data = pickle.loads(packed_data)
    return Point(**data)


# ── Serialization utilities ───────────────────────────────────────────────────-

class Serializable:
    """Simplify serializing arbitrary class instances.

    Adheres to `pickle` protocol v4.
    """

    def to_pickle(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(data: bytes) -> Serializable:
        return pickle.loads(data)

    @classmethod
    def register(cls) -> None:
        global __serializableclass Point:
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

