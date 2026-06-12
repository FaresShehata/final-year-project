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


class Direction(enum.IntEnum):
    NORTH     = 0
    EAST      = 90
    SOUTH     = 180
    WEST      = 270
    NORTHEAST = 45
    SOUTHWEST = 315
    NORTHWEST = 135
    SOUTHEAST = 225


def print_status(status: Status) -> None:
    print(f"status={str(status).lower()}")


print_status(Status.PENDING)
print_status(Status.RUNNING)
print_status(Status.SUCCESS)
print_status(Status.FAILED)
print_status(Status.CANCELLED)


@runtime_checkable
class Nameable(Protocol[K]):
    name: K


@overload
def get_name(nameable: Nameable[K]) -> K: ...


@overload
def get_name(nameable: object) -> str | None: ...


def get_name(nameable: Nameable[str] | object) -> str | None:
    if isinstance(nameable, Nameable):
        return nameable.name
    else:
        return None


class Person(Nameable["Person"]): ...  # type: ignore


person = Person()
person.name = "Alice"


name = get_name(person)
print(name)

name = get_name(object())
print(name)


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Named:
    first_name: str
    last_name: str


@dataclasses.dataclass(slots=True, frozen=True)
class FrozenNamed:
    first_name: str
    last_name: str


frozen_named = FrozenNamed(first_name="Bob", last_name="Smith")


person = Named(first_name="John", last_name="Doe")

print(isinstance(person, Named))
print(isinstance(person, FrozenNamed))


# ── Structural Pattern Matching ───────────────────────────────────────────────

match person:
    case Named(first_name="John", last_name="Doe"): ...
    case Named(last_name="Cooper") as p: ...


match direction := Direction.NORTHWEST:
    case Direction.NORTHWEST:
        print("the cardinal point of the compass")
    case _:
        print("a diagonal point of the compass")


match status := Status.PENDING:
    case Status.PENDING:
        print("still waiting...")
    case Status.RUNNING | Status.SUCCESS:
        print("done!")
        if priority := getattr(status, "_priority", None):
            print(f"PRIORITY={priority}")
    case _:
        raise ValueError(f"unknown status: {status}")


match (direction, value) := (Direction.NORTHWEST, 1.234):
    case (Direction.NORTHWEST, value):
        print(value)
    case (Direction.SOUTH, float(n)):
        print(f"{value} * 2 = {2*n:.1f}")
    case (_, int()):
        print("integer values only please")
    case _:
        print("abort!")


# ── Walrus Operator ───────────────────────────────────────────────────────────

x = None  # type: ignore
y = None  # type: ignore

while x := input():
    y = x.upper()

print(x)
print(y)


# ── Generics ───────────────────────────────────────────────────────────────────

class DictOfDicts(Generic[T, V]): ...


dod = DictOfDicts[int, int]


for key, value in dod.items(): ...


# ── Exception Groups ───────────────────────────────────────────────────────────


try:
    raise ExceptionGroup("Multiple errors occurred.", [
        RuntimeError("Runtime error"),
        ValueError("Value error"),
    ])
except ExceptionGroup as eg:
    print(eg)  # ExceptionGroup['Multiple errors occurred.', 'Runtime error', 'Value error']
    print(eg.exceptions[0])
    print(eg.__cause__)
    print(eg.errors)
    print(eg.messages)
    print(eg.grouped_exceptions)
    print(eg.original_exception)
    print(eg.summary())

    for i in range(0, len(eg.exceptions), 2):
        print(eg[i])


try:
    raise ExceptionGroup("Multiple errors occurred.", [
        RuntimeError("Runtime error"),
        ValueEr<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>        except IndexError:
            return True
        else:
            return False
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return False  # text strings are iterable
    return True


def print_dict(d: dict[str, Any]) -> str:
    lines = []
    if d:
        items = sorted(d.items())
        max_key_len = max(map(len, map(str, d)))
        lines.append("{")
        for k, v in items:
            lines.append(
                f"    {k:{max_key_len}} : {v!r},"
            )
        lines[-1] = lines[-1][:-1]  # remove final comma
        lines.append("}")
    return "\n".join(lines)


