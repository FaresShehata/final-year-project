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


@dataclasses.dataclass
class User:
    username: str
    points: list[Point]
    tasks: list[Task]

    def rank_tasks(self) -> list[Tuple[float, Task]]:
        return sorted((task.priority.value, task) for task in self.tasks)


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str


@dataclasses.dataclass
class _UserPrivateData:
    surname: str
    age: int

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.surname}"


@dataclasses.dataclass(slots=True)
class UserWithPrivateFields:
    first_name: str
    last_name: str
    private_data: _UserPrivateData = dataclasses.field(
        metadata={"private": True}
    )


# ─── Classes ──────────────────────────────────────────────────────────────────

class Notifier:
    def notify(self, message: str) -> None: ...


class EmailNotifier(Notifier):
    def __init__(self, email_address: str) -> None:
        self.email_address = email_address

    def notify(self, message: str) -> None:
        print(f"sending email to {self.email_address}: {message}")
        super().notify(message)


class SmsNotifier(Notifier):
    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number

    def notify(self, message: str) -> None:
        print(f"sending sms to {self.phone_number}: {message}")
        super().notify(message)


class NotificationPlatform(Generic[K]):
    def send_notification(self, key: K, message: str) -> None: ...


class EmailNotificationPlatform(NotificationPlatform[str]):
    def send_notification(self, key: str, message: str) -> None:
        print(f"sending email: {key}, {message}")

#
# class SMSNotificationPlatform(NotificationPlatform[int]):
#     def send_notification(self, key: int, message: str) -> None:
#         print(f"sending sms: {key}, {message}")

#

class NotificationFactory:
    platforms: dict[type[Notifier], NotificationPlatform[Any]]

    def __init__(
        self,
        platform_mapping: dict[
            type[Notifier],
            tuple[Type[NotificationPlatform], ...],
        ],
    ) -> None:
        self.platforms = {
            c: [p(key_type) for p inimport struct
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

print("Bytecode disassemblies")
assert annotated_disassembly(hot_path) == """
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with inspection")
assert annotated_disassembly(inspect.getsource(hot_path)) == """
  3           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               0 (2)
              4 COMPARE_OP               6 (<)
              8 POP_JUMP_IF_FALSE       19
             10 LOAD_FAST                0 (n)
             12 LOAD_FAST                0 (n)
             14 BINARY_MULTIPLY
             16 STORE_FAST               1 (total)
             18 JUMP_ABSOLUTE            5
             21 LOAD_FAST                1 (total)
             23 LOAD_FAST                0 (n)
             25 BUILD_SLICE              1
             27 BINARY_SUBTRACT
             29 STORE_FAST               1 (total)
             31 JUMP_ABSOLUTE            5
             34 LOAD_CONST               1 (None)
             36 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_FALSE': 1, 'BINARY_MULTIPLY': 1, 'STORE_FAST': 2, 'JUMP_ABSOLUTE': 2, 'BUILD_SLICE': 1, 'BINARY_SUBTRACT': 2, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with dis.symtable")
assert annotated_disassembly(dis.symtable(hot_path)) == """
Disassembling hot_path:
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""


# ─────── Code Objects ─────────────────────────────────────────────────────────

def test_code_object() -> None:

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__

    assert co.co_argcount == 3
    assert co.co_varnames == ("x", "y", "z")

    # TODO: add more tests


# ───