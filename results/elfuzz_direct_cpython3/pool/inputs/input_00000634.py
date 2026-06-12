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


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    address: Address

    class Address:
        street: str
        city: City
        zip_code: int

        def get_full_address(self) -> str:
            return f"{self.street}, {self.city.name} {self.zip_code}"

        @classmethod
        def from_street(cls, street: str) -> Address:
            return cls(street=street, city=None, zip_code=0)


class PersonAddress(Address, serialiser): ...
Person.talk_to = "human"

class CatPerson(PersonAddress): ...


# ── Slots ────────────────────────────────────────────────────────────────────

class SlotPerson(Generic[T], metaclass=dataclasses._InitDataclassMeta): ...
SlotPerson.__slots__ = ("name", "age")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def _match_string(s: str) -> str:
    match s.lower():
        case "cat" | "dog":
            return "animal"
        case _:
            return "unknown"


def _match_int(i: int) -> None:
    match i:
        case 1:
            print("one")
        case _ if i == 2:
            print("two")
        case _:
            print("other")


def _match_list(l: list[int]) -> None:
    match l:
        case []:
            print("empty")
        case [1]:
            print("single element")
        case [_, _]:
            print("pair of elements")
        case [a, b, c]:
            print(a * b * c)
        case _:
            print("other")


def _match_empty_dict(d: dict[str, Any]) -> None:
    match d:
        case {}:
            print("empty")
        case {"foo": _, **rest}:
            print(rest)
        case _:
            print("other")


# ── Walrus Operator ──────────────────────────────────────────────────────────

MATCH_CASES: dict[object, object] = {}


def _walrus_operators() -> None:
    while True:
        match input():
            case ["exit"]:
                break
            case [_var:=input()] as exprs:
                print(exprs