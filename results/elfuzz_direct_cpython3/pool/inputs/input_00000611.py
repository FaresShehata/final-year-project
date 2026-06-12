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
    code = dis.Bytecode(hot_path).co_code
    code = code[:6]  # only four opcode bytes are required

    # Build an adder from the 'code' using LOAD_CONST and BINARY_ADD.
    new_fn = types.FunctionType(code, globals(), name="adder", argcount=1)
    new_fn.__doc__ = "__doc__ attribute set by `make_adder_from_bytecode`."
    new_fn.__annotations__["return"] = int
    new_fn._delta = delta  # hacky way to stash extra info on the function
    return new_fn


def patch_math_pow(a: float, b: float, c: float) -> float:
    """Make math.pow special-case integers 0 and 1."""
    if a == 0 or a == 1:
        return a
    if b == 0 or c == 0:
        return 0
    return pow(a, b, c)


math_pow = types.MethodType(patch_math_pow, math)

# ── Structing data ───────────────────────────────────────────────────────────

def pack_integers(*values: int) -> bytes:
    fmt = "<" + "".join(["i" if v < 0 else "I" for v in values])
    return struct.pack(fmt, *values)


def unpack_integers(data: bytes, signed: bool = False) -> list[int]:
    fmt = "<" + "".join(["b" if signed else "B" for byte in data])
    return list(struct.unpack(fmt, data))


# ── Pickling and unpickling ───────────────────────────────────────────────────

def pickle_and_unpickle(obj: Any, protocol=None) -> Any:
    pickled = pickle.dumps(obj, protocol=protocol)
    unfilled = pickle.loads(pickled)
    return unfilled


# ── Copyreg ───────────────────────────────────────────────────────────────────

def my_repr(obj: str) -> str:
    return repr(obj)


class MyPickler(pickle.Pickler):
    def save_str(self, obj: str) -> None:
        self.save_obj(my_repr, obj)


def register():
    pickle.register(MyPickler)


def unregister():
    pickle.unregister(MyPickler)


# ── Marshal ───────────────────────────────────────────────────────────────────

def dump_load() -> None:
    with open("dumped_file.dump", "wb") as f    runtime_checkable,
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
    z: float = 0.0  # default value for keyword argument

    def distance_to_origin(self) -> float:
        """Return the Euclidean distance of a point (x,y,z) to the origin (0,0,0)."""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def magnitude(self) -> float:
        """Return the magnitude or length of a vector."""
        return self.distance_to_origin()

    def dot_product(self, other: Point) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross_product(self, other: Point) -> Point:
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, z={self.z})"


@dataclasses.dataclass(frozen=True, order=False)
class LineSegment(Generic[K]):
    start: K
    end: K
    delta_x: float
    delta_y: float
    delta_z: float = 0.0

    def __post_init__(self):
        assert self.delta_x != 0 or self.delta_y != 0 or self.delta_z != 0, \
               "Line segment must have non-zero direction."

    def _get_step(self, k: K) -> tuple[float, float]:
        if isinstance(k, int):
            return self.delta_x // abs(self.delta_x), self.delta_y // abs(self.delta_y)
        else:
            return self.delta_x / abs(self.delta_x), self.delta_y / abs(self.delta_y)

    def get_steps(self) -> list[tuple[int, int]]:
        steps = []
        step_x, step_y = self._get_step(self.start)  # type: ignore
        while True:
            next_pos = self.start.__add__(step_x, step_y)  # type: ignore
            if next_pos == self.end:
                break
            elif not isinstance(next_pos, (int, float)):
                raise AssertionError("Non-numeric coordinate found in line segment.")
            steps.append((next_pos, None))
            self.start = next_pos
            step_x,