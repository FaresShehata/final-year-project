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
    A = 1
    B = 2


# ── Data structures ───────────────────────────────────────────────────────────

@runtime_checkable
class Sortable(Protocol[K]):
    """Sortable protocol.

    This class defines the contract for classes that can be sorted.
    """

    @classmethod
    def _compare(cls, a: K, b: K) -> int:
        raise NotImplementedError()


def insertionsort(array: list[K], *, compare: Callable[[K, K], int] | None = None) -> None:
    """Insertion sort algorithm."""
    if compare is None:
        compare = Sortable._compare
    n = len(array)
    for i in range(1, n):
        key = array[i]
        j = i - 1
        while j >= 0 and compare(key, array[j]) < 0:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key


@dataclasses.dataclass(frozen=True)
class Item():
    name: str
    weight: float
    value: int

colors = [
    ("red",   0.5),
    ("blue",  0.4),
    ("green", 0.3),
    ("purple", 0.2),
    ("yellow", 0.1),
]


class Color(Sortable["Item"]):

    def __init__(self, **kwargs) -> None:
        super().__setattr__("weight", kwargs["weight"])
        super().__setattr__("value", kwargs["value"])

    def __repr__(self) -> str:
        return f"{self.name}: {self.weight:.2f}, {self.value}"

    def __lt__(self, other: Color) -> bool:
        return self.weight < other.weight


insertionsort(colors)


# ── Generics and protocols ───────────────────────────────────────────────────

class Comparable(Generic[T]):
    ...
    
class ComplexNumber(Generic[T]):
    ...
    
    
async def foo() -> None:
    ...

        
# ── Classes with type variables ───────────────────────────────────────────────

class Suffix(str): 
    def __new__(cls, suffix: str) -> Self:
        instance = str.__new__(cls, "__")  
        instance.suffix = suffix     
        return instance
    
suffix = Suffix("o")


# ── Structural pattern matching ──────────────────────────────────────────────

def handle_error(error: BaseException) -> str:
    match error:
        case IOError(reason=reason, *args):
            print("IOError:", reason)  
            
        case OSError(message=message, *args):
            print("OSError:", message)
            
        case KeyboardInterrupt():
            print("KeyboardInterrupt!")
            
        case _:                      
            print("Some other error!")


# ── Walrus operator ──────────────────────────────────────────────────────────

a: int = 1
b: int = 2
c: int = 3
print(a := b := c := 9)

while True:
    try:
        x = yield from do_something()
    except ValueError:
        ...
    else:
        break
        
for value in it:
    if removed := await remove(value):
        continue
    await process(removed)


# ── Asyncio ──────────────────────────────────────────────────────────────────

loop = asyncio.new_event_loop()

async def async_main() -> None:
    loop.run_until_complete(task())
    
async def task() -> None:
    print("task running...")


loop.create_task(async_main())

event_loop = asyncio.get_running_loop    overload,
    overload_any,
)
from typing_extensions import Annotated, Final, Literal, ParamSpec, Protocol, Self, TypeGuard, TypedDict, get_args, get_origin, get_type_hints, get_type_hints_from_call
from typing_inspect import is_generic_type, is_typeddict

if TYPE_CHECKING or False:
    from typing_extensions import NotRequired, Unpack
else:
    from mypy_extensions import TypedDict, NotRequired, Unpack


# ── Python standard library ──────────────────────────────────────────────────

warnings.filterwarnings(action="ignore", message=".*str object has no .*method?.*")

try:
    import cProfile as Profile
except ImportError:
    import profile as Profile

from multiprocessing import Pool as MultiprocessPool

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait, ALL_COMPLETED
from enum import Enum
from io import StringIO
from itertools import chain, tee
from logging import NullHandler
from os import linesep
from pathlib import Path
from pprint import PrettyPrinter, pformat, pprint, squote
from signal import Signals
from subprocess import    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
