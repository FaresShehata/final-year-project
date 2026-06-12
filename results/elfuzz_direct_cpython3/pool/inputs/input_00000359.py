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

# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclass(order=True)
class Item:
    priority: int
    value: str

items = [
    Item(priority=1, value="B"),
    Item(priority=2, value="A"),
]

assert items[0].value == "A"


# ── Generics ───────────────────────────────────────────────────────────────────

async def gen_func() -> int:
    await asyncio.sleep(random.random())
    return 42

def generic_class_demo():
    t1 = gen_func()
    t2 = gen_func()

    assert isinstance(t1, int)
    assert isinstance(t1, (int, Awaitable))
    assert isinstance(t2, int)


class Counters(Generic[T]):
    def __init__(self, init_counter: dict[K, V], max_size: int) -> None:
        self.counter: Counter[V]
        self.max_size: int
        
        self.counter = Counter(init_counter)
        self.max_size = max_size

    @classmethod
    def from_dict(cls, init_counter: dict[K, V], max_size: int) -> Counters[K, V]:
        counter = cls.__new__(cls, init_counter, max_size)
        counter.counter = Counter(init_counter)
        counter.max_size = max_size
        return counter

    def add(self, key: K, count: V) -> None:
        self.counter[key] += count
        if len(self.counter) > self.max_size:
            rv = sorted([(self.counter[k], k) for k in self.counter],
                        reverse=True)[:self.max_size]
            del self.counter[self.counter.keys()[rv[-1][1]]]


# ── Slots ──────────────────────────────────────────────────────────────────────

class PersonProto:
    name: str
    age: int
    height: float
    weight: float

    def __repr__(self) -> str:
        return f"Person(name={self.name}, age={self.age})"

class Person(PersonProto, metaclass=dataclasses.DataClassMeta):
    __slots__: ClassVar[tuple[str, ...]] = ()

person_proto = PersonProto(name='John', age=30, height=1.75, weight=68.0)
print(person_proto)

p = Person(name='Jane', age=29, height=1.65, weight=70.0)
printdef ctypes_demo():
    a_addr = id(C())
    c = A.from_address(a_addr)

    # Unpack fields in native format to check they're the same as the original.
    assert a_addr == c.x
    assert c.y[0] == ord("A")

    for base in [A, B, C]:
        assert base._fields_
        assert not any(len(f[1]) > 1 for f in base._fields_)
        assert hasattr(base, "_anonymous_") is False
        assert hasattr(base, "_bitfield_") is False


def struct_demo():
    class A(struct.Struct):
        _fields_ = [("x", "i"),
                    ("y", "c", 2)]
    
    assert A.sizeof == 5   # 4 bytes for x, 2 bytes for y
    
    a = A.pack(-1, b"\0\0")
    a = A.unpack(a)
    assert a[0] == -1
    assert a[1] == b"\0\0"
    
    assert len(a) == 5       # actually returns tuple of unpacked values


# ── Array ─────────────────────────────────────────────────────────────────────

arr = array.array('h')
print(arr.typecode)  # 'h'
arr.append(1)
arr.extend([2, 3])
print(arr.tolist()) 