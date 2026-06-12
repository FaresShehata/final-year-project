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
    LOWEST = -99
    HIGH = 99

    @classmethod
    def from_str(cls, priority: str) -> Priority:
        try:
            return cls[priority.upper()]
        except KeyError as exc:
            raise ValueError(f"unknown priority '{priority}'") from exc

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


PRIORITY_REPR_STRINGS = {
    Priority.LOWEST : "-99",
    Priority.HIGH   : "+99",
}

PRIORITY_ORDERED_VALUES = tuple(Priority[p] for p in ("LOWEST", "HIGH"))

# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Node(Generic[K]):
    key: K                    # unique identifier for node
    value: V                  # data associated to key
    priority: Priority        # priority within a partition
    prev: Node|None = None    # link to previous node in tree
    next: Node|None = None    # link to next node in tree

    def insert_after(self, after: Node) -> None:
        assert after.priority >= self.priority
        old_next = after.next
        after.next = self
        if old_next is not None:
            old_next.prev = self
        self.prev = after
        self.next = old_next

    def delete(self) -> None:
        prev = self.prev
        next = self.next
        if prev is not None:
            prev.insert_after(next)
        elif next is not None:
            next.prev = None
        else:
            pass  # self was root of linked-list

    def __post_init__(self) -> None:
        if self.key is None or self.value is None:
            raise ValueError("'key' and 'value' must be defined")


class PriorityQueue(Generic[T], metaclass=ABCMeta):

    def __init__(self) -> None:
        self.root: Node | None = None
        self.size: int = 0

    @abstractmethod
    def _find_node(self, item: T) -> Iterator[Node]: ...

    @overload
    def __contains__(self, item: T) -> bool:
        ...       # ordered by default

    @overload
    def __contains__(self, item: Tuple[Prioriry, T]) -> bool:
        ...       #import marshal
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

    source_code = fn.co_code
    loop_count = fn.co_nlocals
    name_index = fn.co_name.encode('utf-8')
    names = fn.co_names[:]
    constants = fn.co_consts[:]

    new_source_code = bytearray(source_code)
    new_constant_pool = []

    for i in range(loop_count):
        oparg = loop_count - i
        opcode = dis.OPCODES[source_code[oparg]]
        code = opcode.new_argument(source_code, oparg)
        new_source_code.extend(code)
        if opcode.code_offset + len(code) != source_code[oparg + 1]:
            raise ValueError("impossible loop size")
        arg = new_source_code[opcode.code_offset : opcode.code_offset + code[-1]]

        if opcode == dis.HALT:
            break
        elif opcode in (dis.STORE_NAME, dis.STORE_GLOBAL):
            index = ord(arg) + 1
            name = names[index]
            new_source_code[opcode.code_offset+1] = name.index(name_index)

        elif opcode == dis.GET_ITER:
            if arg in (256, 257):  # list/set/tuple/dict comprehensions
                next_stmt_index = dis.DISASSEMBLER.findnext(new_source_code, arg)
                next_arg = new_source_code[next_stmt_index]
                next_opcode = dis.OPCODES[next_arg]
                if next_opcode.code_offset == arg + 1:
                    # this is a nested comprehension
                    continue

        elif opcode in (dis.BUILD_SET, dis.BUILD_LIST, dis.BUILD_TUPLE):
            constant_index = arg // 256 + 1
            constant_name = constants[constant_index].decode('utf-8')
            
            if opcode == dis.BUILD_SET:
                new_source_code[arg] = ord(constant_name)
                
            elif opcode == dis.BUILD_LIST:
                if constant_name.count(',') == len(constant_name.split(',')):
                    # list literal
                    new_source_code[arg] = ord(constant_name)
                    
                else:
                    # compound list
                    new_constant_pool.append(constants[constant_index])
                    new_source_code[arg] = ord(new_constant_pool[-1])

            elif opcode == dis.BUILD_TUPLE:
                if ',' in constant_name:
                    # tuple literal
                    new_source_code[arg] = ord(constant_name)
                else:
                    # composite tuple
                    new_constant_pool.append(constants[constant_index])
                    new_sourceT = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

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
    
    def __bool__(self) -> bool:
        return True
    
    
# ── Concrete classes ───────────────────────────────────────────────────────────

class Square(Shape):

    side_length: float = TypedDescriptor(float, 2 <= ...)

    def __init__(
        self,
        side_length: float = 1,
        color: str = "green",
    ):
        super().__init__(color=color)
