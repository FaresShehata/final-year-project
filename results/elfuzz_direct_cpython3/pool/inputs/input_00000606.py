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
class Comparable(Protocol[K]):
    def compare_to(self, other: K) -> int: ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=True)
class Person:
    name: str
    age: int
    gender: str
    address: Address


@dataclasses.dataclass(init=False, order=True, frozen=True)
class Address:
    street: str
    city: str
    state: str

    def __init__(self, street: str, city: str, state: str):
        super().__init__()
        self.street = street
        self.city = city
        self.state = state


p = Person("Mickey", 45, "Male", Address("Main St.", "San Francisco", "CA"))


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotPerson:
    name: str
    age: int
    gender: str
    address: Address


s_p = SlotPerson("Minion", 12, "Female", Address("Rue des Petits-Risques", "Paris", "FR"))
# AttributeError: 'SlotPerson' object has no attribute '__dict__'

# ── Structural pattern matching ──────────────────────────────────────────────

@overload
def match(value: T, *cases: tuple[object, V]) -> V: ...
@overload
def match(value: T, *cases: tuple[object, V], default: V) -> V: ...
@overload
def match(value: T, **cases: tuple[V]) -> V: ...

def match(value: T, *cases: tuple[object, V], default: V = ...) -> V:
    for case_value, case_result in cases:
        if value == case_value:
            return case_result
    if default is ...:
        raise ValueError(f"No case matched on {value}")
    return default


person = {
    "name": "Mickey",
    "age": 45,
    "gender": "Male",
    "address": {"street": "Main St.", "city": "San Francisco", "state": "CA"},
}

match person:
    case {"name": name, "age": age} as p if age > 18:
        print(p.name)
    case {"name            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
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


# ── dis and bytecodes ─────────────────────────────────────────────────────────

def show_opcodes(fn: types.FunctionType, count: int = 1000) -> None:
    """Print the first 'count' op codes of the function's bytecode."""
    dis.disassemble(fn, count=count)


def show_and_compare(opcodes_1: bytes, opcodes_2: bytes) -> None:
    diff = opcodes_1.decode("ascii") != opcodes_2.decode("ascii")
    print(diff)
    if not diff:  # pragma: no cover
        return

    label_width = max(len(name) for name in opcodes_1.splitlines())

    def _print(line: str) -> None:
        s_line = line.ljust(label_width, " ")
        print(s_line.rstrip(), end="")
        for part in line.split():
            if part.isdigit():  # Assume it's a register number.
                print(Color.BLUE.echo(f"({part}) "), end="")  # pylint: disable=W0511
            else:
