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

print(annotated_disassembly(lambda x: x + 1))

# ── dis module ────────────────────────────────────────────────────────────────

for i in range(ord("a"), ord("z") + 1):
    print(f"ord({i}): {dis.opname[i]}")
    print(f"{i}: {dis.opname[i]}")


# ── Code Objects ──────────────────────────────────────────────────────────────


def func(a, b):
    pass


assert func.__code__.co_argcount == 2

func_code = func.__code__
assert isinstance(func_code.co_consts, tuple)

assert len(func_code.co_names) > 56

# ── ctypes ────────────────────────────────────────────────────────────────────

intp_t = ctypes.POINTER(ctypes.c_int)

s = struct.Struct("<hh")
v = s.pack(7, 11)
print(v)
print(struct.unpack_from(s.format, v))  # <- unpack_to



# ── Array ─────────────────────────────────────────────────────────────────────

# py3k
arr = array.array("b", [0])
arr.append(-99)
arr.extend([-11, -12])

# py2x
arr = array.array('b', [0])
arr.append(-99)
arr.extend((-11, -12))


# ── MemoryView ───────────────────────────────────────────────────────────────

mem_v = memoryview(arr).cast("B")

arr[0] += mem_v[0]
print(mem_v[0], arr[0])


# ── Pickle ───────────────────────────────────────────────────────────────────

pickle_str = pickle.dumps(["hello", True, None, 42])  # <1>

# The following line will raise an error, because the `date` class has been
# removed from Python's standard library.
# date = datetime.date(2021, 12, 10)               # <2>
# pickle.dump(date, open("obj.pkl", "wb"))

with open("obj.pkl", "rb") as fp:
    obj = pickle.load(fp)                          # <3>
    print(obj)

arr = array.array("d", [-2.1, -3.1, -4.1])
pickle.dump(arr, open("arr.pkl", "wb"))            # <4>


with open("arr
    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius
        self.perimeter()                             # type: ignore[attr-defined]


@dataclass(slots=True, frozen=True)
class Point:
    x: int | float = field(compare=False)      # type: ignore[misc]
    y: int | float = field(compare=False)      # type: ignore[misc]

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass(eq=True, kw_only=True, frozen=True)
class Path:
    start: Point
    end: Point
    length: float = field(repr=False, compare=False)

    def distance(self) -> float:
        dx, dy = self.end.x - self.start.x, self.end.y - self.start.y
        return sqrt(dx * dx + dy * dy)



# ── CopyReg │ __weakref__ ─────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True, frozen=True)
class CustomObject:
    a: int
    b: str

    def __repr__(self) -> str:
        return textwrap.dedent(
            """
            CustomObject(a=<{a}>, b="{b}")
            """.format_map(vars(self))
        )

custom_obj = CustomObject(1, "foo")


class CustomWeakRef(weakref.ref):

    def __call__(self) -> CustomObject:
        if ref := self():
            if not ref.a or not ref.b:
                del ref.a, ref.b
                del custom_obj
                del ref
            return ref
        else:
            del custom_obj
            del ref
            return None

referred_ref = CustomWeakRef(custom_obj)

custom_obj.a = 42
print(referred_ref())

del referred_ref
gc.collect()


# ── Weakref ───────────────────────────────────────────────────────────────────

my_weakref = weakref.ref(my_object)


def deref(ref: weakref.ref) -> Any | None:
    try:
        return ref()
    except TypeError:
        return None


class A:
    def foo(self) -> None:
        print(A.foo)
        print(A.foo())


A.bar = lambda self: print("bar")
A().foo()
A().bar()



# ── Struct ────────────────────────────────────────────────────────────────────


def my_struct_class(fmt: str, size: int) -> type[Any]:
    """Create a custom struct subclass."""

    class MyStruct(TypeVar):
        bytestring = bytes(size)

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
            priority=getattr(Priority, data["priority"]),
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )


@dataclasses.dataclass(frozen=True, order=True, slots=True)
class NamedTuplePoint(Point): ...  # type: ignore # https://github.com/python/mypy/issues/7396

@dataclasses.dataclass(frozen=True, order=True, slots=True)
class MyDataClass:
    tag: str
    value: int
    timestamp: float = dataclasses.field(default_factory=time.time)


# ── Slots ────────────────────────────────────────────────────────────────────

class Node(Generic[K]):
    parent: Node[K] | None = None

    def __init__(self, value: K) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class BinaryNode(Node[int]):
    left_child: BinaryNode[int] | None = None
    right_child: BinaryNode[int] | None = None

    def insert(self, value: int) -> None:
        if value < self.value:
            if not self.left_child:
                self.left_child = BinaryNode(value)
