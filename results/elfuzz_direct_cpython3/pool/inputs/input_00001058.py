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

@runtime_checkable
class Deserialisable(Protocol):
    @classmethod
    def from_dict(cls, d: dict[str, any]) -> T: ...


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Path:
    path: str
    size: int
    depth: int

    @property
    def absolute_path(self) -> str:
        return f"/{self.path}"


@dataclasses.dataclass(frozen=False)
class Person:
    name: str
    age: int
    address: Address
    phone_numbers: list[str]
    children: tuple[Person] = ()

    def add_child(self, new_children: Person) -> None:
        self.children += (new_children,)


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str


# ─── Slots & Hashing ─────────────────────────────────────────────────────────

# class FooSlotOnly:
#     __slots__ = ["x"]
#
# @overload
# def hash(obj: FooSlotOnly) -> int: ...
# @overload
# def hash(obj: FooSlotOnly) -> NotImplemented: ...
#
# def hash(obj: FooSlotOnly) -> int | NotImplemented:
#     if hasattr(obj, "__slots__"):
#         raise TypeError("__hash__ not implemenetd on non-hashable type")
#     else:
#         return id(obj)
#
# @dataclasses.dataclass(slots=True)
# class FooSlotDataClass:
#     x: int
#
# @dataclasses.dataclass(slots=True, frozen=True)
# class FooSlotFrozenDataClass:
#     x: int
#
#
# class BarSlot:
#     __slots__ = ['x']
#     def __init__(self, x: int):
#         self.x = x
#
#
# class BazSlot:
#     __slots__ = ('x', 'y')
#     def __init__(self, x: int, y: int):
#         self.x = x
#         self.y = y
#

# ─── Struct Pattern Matching ─────────────────────────────────────────────────

def match_thing(thing: any) -> any:
    match thing:
        case Person(name="Alice", age=3