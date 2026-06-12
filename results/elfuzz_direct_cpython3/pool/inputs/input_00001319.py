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
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    Union,
    cast,
)


if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import MessageTypeDef
else:
    MessageTypeDef = object


a: bytes = b"\x00\x01"

assert a + (1,) != 1

b: bytearray = bytearray()

assert a + b != b"\x00\x01"

c: list[int] = []

assert a + c != []

d: tuple[str, ...] = ()

assert a + d != ("",)

e: set[str] = set()

assert a + e != frozenset(e)

f: dict[float, str] = {}

assert a + f != {1.23: "abc"}

g: deque[int] = deque()

assert a + g != deque([1])

h: range[bool] = range(True)

assert a + h != range(False)

i: complex = 1j

assert a + i != 1j

j: memoryview = memoryview(b"")

assert a + j != memoryview(b"")

k: float = 1.23

assert a + k != 1.23

l: int = 1

assert a + l != 1

m: slice = slice(None, None, None)

assert a + m != slice(None, None, None)

n: str = "1"

assert a + n != "1"

o: tuple[float, ...] = ()

assert a + o != (1.23,)

p: tuple[float, float] = (1.23,)

assert a + p != (1.23, 1.23)

q: tuple[float, float, float] = (1.23, 1.23, 1.23)

assert a + q != (1.23, 1.23, 1.23)

r: tuple[float, float, float, float] = (1.23, 1.23, 1.23, 1.23)

assert a + r != (1.23, 1.23, 1.23, 1.23)

s: tuple[float, ...] = (1.23, 1.23, 1.23, 1.23)

assert a + s != (1.23, 1.2
try:
    assert a + {"one": b"\x00\x01"}
except TypeError:
    pass

try:
    assert a + ((1,),)
except TypeError:
    pass

try:
    assert a + {(1): b"\x00\x01"}
except TypeError:
    pass

print(len(list(range(4))), len(tuple(range(4))))

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + {}
except TypeError:
    pass

try:
    assert a + []
except TypeError:
    pass

try:
    assert a + dict(one=b"\x00\x01")
except TypeError:
    pass

print(a)

try:
    assert a + b""
except TypeError:
    pass

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + ""
except TypeError:
    pass

print(a * 2)

try:
    assert a * (-2,)
except TypeError:
    pass


def unknown_function() -> int:
    ...


try:
    assert a * unknown_function()
except TypeError:
    pass

try:
    assert a / unknown_function()
except TypeError:
    pass

try:
    assert a // unknown_function()
except TypeError:
    pass

try:
    assert a % unknown_function()
except TypeError:
    pass

try:
    assert a ** unknown_function()
except TypeError:
    pass

try:
    assert a & unknown_function()
except TypeError:
    pass

try:
    assert a | unknown_function()
except TypeError:
    pass

try:
    assert a ^ unknown_function()
except TypeError:
    pass

try:
    assert a << unknown_function()
except TypeError:
    pass

try:
    assert a >> unknown_function()
except TypeError:
    pass

print(ord("\n"))

try:
    assert ord("\n") < 0
except ValueError:
    pass

try:
    assert chr(-1) == " "
except ValueError:
    pass

try:
    assert chr(32768) == "⠀"
except ValueError:
    pass

try:
    assert chr(1_000_000) == "⣾"  # ⠿
except ValueError:
    pass

try:
    assert chr(0x10FFFF) == "􏿿"
except ValueError:
    pass

try:
    assert chr("A") == "\u0041"
except TypeError:
    pass

try:
    assert chr((1)) == "\u0001"
except TypeError:
    pass

try:
    assert chr(<PASSWORD>) == "\u1F600"
except TypeError:
    pass

try:
    assert chr(Priority.LOW.value) == "LOW"
except ValueError:
    pass

try:
    assert chr(-Priority.LOW.value) == "HIGH"
except ValueError:
    pass

try:
    assert chr(Priority.URGENT.value) == "URGENT"
except ValueError:
    pass

try:
    assert chr(Priority.HIGH.value) == "HIGHEST"
except ValueError:
    pass

try:
    assert chr(FooBar.BAR.value) == "BAR"
except ValueError:
    pass

try:
    assert chr(Flag.RWX.value) == "RWX"
except ValueError:
    pass

assert chr(dataclasses.FIELDS["id"].metadata["repr"]) == "<field>"

tup: tuple[float, ...] = (1.23,)

print(tup[0], tup[-1])

try:
    print(tup[:])
    print(tup[tuple()])
    print(tup[tuple(x for x in range(len(tup)))])
except TypeError as exc:
    print(exc)

###############################################################################

class Foo:
    bar: int

    def __init__(self, bar: int) -> None:
        self.bar = bar

    def bar(self) -> int:
        return self.bar

    def baz(self, bar: int) -> int:
        return self.bar + bar


foo: Foo = Foo(bar=1)

bar: int = foo.bar()

baz: int = foo.baz(bar=1)

class Baz(Foo):
    def quux(self, baz: int) -> int:
        return self.baz(baz) + 2

baz_quux: int = Baz().quux(baz=1)

try:
    baz_quux = Baz().quux(foo.bar())
except AttributeError:
    pass

###############################################################################

class Status(enum.Enum):
    PENDING  = enum.auto()
    RUNNING  = enum.auto()
    COMPLETED = enum.auto()
    ERROR    = enum.auto()


@enum.unique
class Mode(enum.Enum):
    ALL      = enum.auto()
    SOME     = enum.auto()
    NONE     = enum.auto()
    UNKOWN   = enum

def runtime_checkable_with_over

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
