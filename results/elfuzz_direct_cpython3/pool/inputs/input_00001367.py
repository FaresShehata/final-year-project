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


@dataclasses.dataclass(order=True, frozen=True, order_using=lambda obj: (obj.x, obj.y))
class FrozenPoint(Point): ...


@dataclasses.dataclass(order=True, frozen=True, repr=False, eq=False, order_using=lambda obj: obj.x)
class ComparableFrozenPoint(FrozenPoint): ...


@dataclasses.dataclass(frozen=True)
class UnserialisableDataclass:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class SerializableDataclass:
    name: str
    age: int

    def to_dict(self) -> dict[str, any]: ...
    @classmethod
    def from_dict(cls, data: dict) -> SerializableDataclass: ...


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotDataclass:
    a: int
    b: int
    c: int

    def __post_init__(self):
        assert isinstance(self.a, int), f"Expected `a` to be an integer but got `{type(self.a).__name__}`."
        assert isinstance(self.b, int), f"Expected `b` to be an integer but got `{type(self.b).__name__}`."
        assert isinstance(self.c, int), f"Expected `c` to be an integer but got `{type(self.c).__name__}`."

    def __repr__(self) -> str: ...


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(obj: any) -> None:
    if isinstance(obj, list):
        print("Is a list.")
    elif isinstance(obj, tuple):
        print("Is a tuple.")
    else:
        print("Not a list or tuple.")

match([3, 4])  # Is a list.
match((3, 4))  # Is a tuple.


# ── Walrus Operator ───────────────────────────────────────────────────────────

d: dict[int, int] = {}
for i in range(10):
    d[i] = i ** 2  # Not valid before Python 3.8.
    d := {i: i ** 2}  # Valid since Python 3.8.

print(d)


# ── Exception Groups ──────────────────────────────────────────────────────────
try:
    raise ValueError("First error")
except ValueError:
    try:
        raise TypeError("Second error")  # Second error overrides first error's traceback.
    finally:
        raise RuntimeError("Third error")  # Third error doesn't override second's traceback.
except Exception as e:
    print(e.__traceback__.tb_frame.f_globals)  # Prints the globals dictionary of the module where the original exception was raised.
    print(ExceptionGroup("Multiple errors", [e]))  # Prints all three exceptions.
else:
    print("No exception occurred.")


# ── Exception Group's Tracebacks ─────────────────────────────────────────────
eg = ExceptionGroup("Multiple errors", [
    ValueError("First error"),
    TypeError("Second error"),  # Second error overrides first error's traceback.
    RuntimeError("Third error"),  # Third error doesn't override second's traceback.
])
print(repr(eg))


# ── Exception Group's Stack Frames ────────────────────────────────────────────
eg = ExceptionGroup("Multiple errors", [
    ValueError("First error"),
    TypeError("Second error"),  # Second error overrides first error's traceback.
    RuntimeError("Third error"),  # Third error doesn't override second's traceback.
])
print(eg.__cause__)

eg.__cause__ = ExceptionGroup("Nested errors", [
    ValueError("Nested First error"),
    TypeError("Nested Second error"),
])

eg.__traceback__ = eg.__cause__.__traceback__

print(eg.__cause__)


# ── Revoke lsblk's output ─────────────────────────────────────────────────────
lsblk_output = """
NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
loop0                     7:0    0   993M  1 loop /snap/core18/1916
loop1                     7:1    0  1001M  1 loop /snap/s    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeAlias,
    Union,
)

from . import typing_extras





""" 🥑 Types """

# ╭── String ───────────────────────

_TypeString = TypeVar("_TypeString", bound=str, covariant=True)



# ╰── Int ─────────────────────────

_TypeInt = TypeVar("_TypeInt", bound=int, covariant=True)





# ╭── Function ─────────────────────

_Function = TypeVar("_Function", bound=Callable[..., Any])



# ╰── Tuple ────────────────────────
TupleStrAny: TypeAlias = tuple[str, ...]






""" 🍎 Generics """

# ╭── Generic ──────────────────────

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


class Generic(Tuple[Union[_T1, _T2, _T3, _T4]]):
    pass




# ╰── Generic with extra methods ─────

_T5 = TypeVar("_T5", bound="Generic[...]")
_T6 = TypeVar("_T6", bound="Generic[...]")

_GenericWithMethod: TypeAlias = TypeVar(
    "_GenericWithMethod",
    bound="Generic[Optional[_T5], Optional[_T6]]"
)




# ── class MyClass ───────────────────────────────────────────────────────────

_TypingExtras = TypeVar("_TypingExtras", bound="typing_extras.TypingExtras")

class TypingExtras(_TypingExtras):
    pass


# ── class MyClass ────────────────────────────────────────────────────────────

_T5 = TypeVar("_T5", bound="MyClass[String]", covariant=True)
_T6 = TypeVar("_T6", bound="MyClass[Int]", contravariant=True)


class MyClass[T7](Generic[T7]):
    def __init__(self, arg: T7) -> None:
        self.arg: T7 = arg
    
    @classmethod
    def of(cls: type["_T5"], *args: T7) -> _T5:
        return cls(args) # type: ignore
    


# ── class MySubclass ─────────────────────────────────────────────────────────

_T7 = TypeVar("_T7")

class MySubclass(MyClass[_T7], Generic[_T7]):
    pass


# ── class MyClassWithExtraMethods ────────────────────────────────────────────

class MyClassWithExtraMethods:
    def __init__(self, arg: int) -> None:
        self.arg: int = arg

    def add(self, other: int) -> int:
        return self.arg + other



# ── class BaseClass ─────────────────────────────────────────────────────────