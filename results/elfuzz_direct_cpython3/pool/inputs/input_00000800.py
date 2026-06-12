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
            "metadata": self.metadata,
            "_history": [h.value for h in self._history],
        }

    @classmethod
    def from_dict(
        cls, d: dict[str, T], *, default_priority: Priority = Priority.NORMAL
    ) -> Task:
        task_id = d["id"]
        task_name = d["name"]

        try:
            task_priority = getattr(Priority, d["priority"]).value
        except KeyError as e:
            raise ValueError(f"Invalid priority: {e}") from e

        task_tags = d.get("tags") or []
        task_metadata = d.get("metadata") or {}
        task_history = d["_history"] or []

        task = cls(
            task_id,
            task_name,
            task_priority,
            Status(task_history[-1]),
            task_tags,
            task_metadata,
        )

        return task


# ── Structs ───────────────────────────────────────────────────────────────────

MyStruct = struct.Struct("<ii")


# ── Collections ───────────────────────────────────────────────────────────────

class MySet(set[int]):
    pass


class MyDict(dict[K, V]):

    def __init__(
        self,
        iterable: Iterable[Tuple[K, V]],
        *,
        init: bool = False,
        fillvalue: V = None,
        mapfunc: Callable[[K, V], tuple] = None,
    ):
        super().__init__()
        self.fillvalue = fillvalue
        self.mapfunc = mapfunc
        for k, v in iterable:
            self.add(k, v)

    def add(self, key: K, value: V) -> None:
        if self.mapfunc:
            key, value = self.mapfunc(key, value)
        self[key] = value

    def keys(self) -> Iterator[K]:
        return iter(super().keys())

    def values(self) -> Iterator[V]:
        return iter(super().values())

    def items(self) -> Iterator[tuple[K, V]]:
        return iter(super().items())


# ── Generics ──────────────────────────────────────────────────────────────────

class MyGeneric(Generic[T]):
    def foo(self, t: T) -> str:
        return f"{t}"


class MyUnion(Generic[T | V]):
    def foo(self, t_or_v: T | V) -> str:
        return f"{t_or_v}"


# ── Exceptions ─────────────────────────────────────────────────────────────────

class MyException(Exception):
    ...


class MyError(Exception):
    ...

class MyCustomError(MyError):

    def __init__(self, msg: str, extra_info: dict) -> None:
        super().__init__(msg)
        self.extra_info = extra_info



# ── Walrus Operator ───────────────────────────────────────────────────────────

counter = Counter(a=1, b=2)

print((counter[a := "c"] := 2))


# ── Named Tuple ─

# ── Disassembler utility functions ────────────────────────────────────────────

def get_function_bytecode(fn) -> bytes:
    return marshal.dumps(dis.Bytecode(fn).to_bytes())


def pretty_marshal(data, indent=0) -> str:
    lines = pickletools.optimize(
        pickle.dumps(marshall.loads(data), protocol=-1))
    out = ""
    for line in lines:
        if isinstance(line, pickle.PickleableScalar):
            out += f"{' ' * indent}{line}\n"
        elif isinstance(line, pickle.ExtType):
            out += (
                f'{" " * indent}b{line.code} '
                f'type {hex(line.type)}\n'
            )
        else:
            out += f'{line}'
    return out.strip()


# ── Code object utilities ─────────────────────────────────────────────────────

def get_code_object(fn) -> types.CodeType:
    return fn.__code__

def dump_code_object(code) -> str:
    # NB: `dis` function doesn’t work with only the code object (it needs to be an
    #     instance of a code type).
    code_obj = types.CodeType(
        code.co_argcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,
        code.co_consts,
        code.co_names,
        code.co_varnames,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )
    return annotated_disassembly(code_obj)


# ── Low-level types and operations ────────────────────────────────────────────

def test_ctypes():
    return ctypes.c_int32(789456123) == ctypes.c_ulonglong(789456123)

def test_struct():
    x = array.array('i', [789456123])
    print(x.itemsize)
    
    return struct.unpack('>I', b'\x7\x8\x9\x4\x5\x6\x1\x2')[0]

def test_pickle():
    x = array.array('i', [789456123])

    data = pickle.dumps(x)
    print(pretty_marshal(data))

    y = pickle.loads(data)
    assert x.tolist() == y.tolist()

    z = bytearray([1, 2, 3])
    data = pickle.dumps(z)
    w = pickle.loads(data)
    assert list(w) == [1, 2, 3]


# ── Memoryview utilities ──────────────────────────────────────────────────────

def test_memoryview():
    x = array.array('u')
    x.frombytes(b"Hello world!\0")
    mv = memoryview(x)
    mv[1::2].readonly = True
    assert mv.readonly is True


# ── Pickle tools utility functions ────────────────────────────────────────────

def show_opcode_table(opcodes=None):
    """
    Display opcode table.
    """
   