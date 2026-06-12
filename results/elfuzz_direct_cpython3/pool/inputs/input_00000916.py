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


@dataclasses.dataclass(eq=True, order=True)
class Student:
    name: str
    age: int
    grades: list[float]

    def average_grade(self) -> float:
        return sum(self.grades) / len(self.grades)


@dataclasses.dataclass(slots=True)
class Person:
    """Class with private attribute."""

    _name: str

    def get_name(self) -> str:
        return self._name.upper() if self._name else ""

    def set_name(self, new_name: str) -> None:
        self._name = new_name[:255]

    def __repr__(self) -> str:
        return f"<Person(name={self.get_name()}, ...>"

    def __str__(self) -> str:
        return f"Name: {self.get_name()}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotObject(object):
    __slots__ = ["_x", "_y"]

    def __init__(self, x: float, y: float) -> None:
        super().__setattr__("_x", x)
        super().__setattr__("_y", y)

    def __getitem__(self, index: int) -> float:
        return (self._x, self._y)[index]


# ── Generics ──────────────────────────────────────────────────────────────────

class Registry(Generic[T]):
    def __init__(self) -> None:
        self._registry: dict[K, T] = {}

    def register_one(self, key: K, item: T) -> None:
        assert key not in self._registry, f"duplicate registration for key '{key}'!"
        self._registry[key] = item

    def register_many(self, items: Iterable[tuple[K, T]]) -> None:
        for key, item in items:
            self.register_one(key, item)

    def unregiser_one(self, key: K) -> None:
        del self._registry[key]

    def unregister_all(self) -> None:
        self._registry.clear()

    def lookup(self, key: K) -> T:
        return self._registry[key]


class Registry2(Generic[T]):
    def __init__(self) -> None:
        self._registry: dict[K, T] = defaultdict(list)

    def register(self, key: K, item: T) -> None:
        self._registry[key].append(item)

    def lookup(self, key: K) -> T:
        return random.choice(self._registry[key])


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_and_handle(data: dict) -> tuple[bool, list[int]]:

    # Match on `data` type.
    match data:
        case {"type": "point", "x": x, "y": y} as point_data:
            print(f"Point: ({x}, {y})")
            return True, [x, y]

        case {"type": "student", "age": age, "grades": grades} as student_data:
            print(f"Student: {student_data['name']} ({age}): {grades}")
            return False, []

        case _:
            raise ValueError("Unknown entry!")


def match_on_type(data: dict) -> None:
    # Match on `data` type.
    match data["type"]:
        case "point":
            print("It's a point!")

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
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

