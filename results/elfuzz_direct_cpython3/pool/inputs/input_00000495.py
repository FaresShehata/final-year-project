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

    def get_distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
    

PointList = list[Point]


@dataclasses.dataclass(frozen=True)
class LineSegment:
    point_a: Point
    point_b: Point

    @property
    def length(self) -> float:
        dx = self.point_a.x - self.point_b.x
        dy = self.point_a.y - self.point_b.y
        return (dx**2 + dy**2)**0.5
    
    def intersects(self, other: LineSegment) -> bool:
        return False


def create_point_list(n: int) -> PointList:
    return [Point(x=random.random(), y=random.random())
            for _ in range(n)]


# ── Slots ────────────────────────────────────────────────────────────────────

class Person:
    __slots__ = ("firstname", "lastname", "age")

    def __init__(self, firstname: str, lastname: str, age: int) -> None:
        self.firstname = firstname
        self.lastname = lastname
        self.age = age

    
class Employee(Person):
    __slots__ = ("company", "position")
    
    def __init__(self, firstname: str, lastname: str, age: int, company: str, position: str) -> None:
        super().__init__(firstname=firstname, lastname=lastname, age=age)
        self.company = company
        self.position = position


# ── Structural Pattern Matching ───────────────────────────────────────────────

async def task(a: int, b: int) -> int:
    await asyncio.sleep(random.random() / 4)
    result = a * b
    print(f"Task with args {a} and {b}: ", end="")
    return result


async def main_01() -> None:
    tasks = [
        task(a=i, b=j)
        for i in range(6)
        for j in range(i+1, 7)
    ]
    start_time = time.monotonic()

    results = []
    for future in asyncio.as_completed(tasks):
        res = await future
        results.append(res)
        print(res)

    elapsed_time = time.monotonic() - start_time
    print(f"\n{elapsed_time:.9f}s")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def main_02() -> None:
    results = []
    for future in asyncio.as_completed([task(a=i, b=j) for i in range(6) for j in range(i+1, 7)]):
        result = await future
        results.append(result)
        print(result)

    print(sum(results))


# ── Typing Generics ───────────────────────────────────────────────────────────

class Node(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value


class BinarySearchTree(Generic[T]):
    def __init__(self, root: Node[T]) -> None:
        self.root = root

    def insert(self, node: Node[T], parent: Node[T] | None = None) -> None:
        if not parent:
            parent = self.root
        
        if node.value < parent.value:
            if parent.left_child:
                self.insert(node=node, parent=parent.left_child)
            else:
                parent.left_child = node
        elif node.value >= parent.value:
            if parent.right_child:
                self.insert(node=node, parent=parent.right_child)
            else:
                parent.right_child = node
            
        # TODO: insert into appropriate subtree


# ── Exception Groups ──────────────────────────────────────────────────────────

def raise_exception_group(name: str) -> None:
    group = ExceptionGroup(name=name, exceptions=[ValueError("value error"), KeyError("key error")])
    raise group



    for line in bytecode.splitlines():
        if line.startswith("#"):
            comment_lines.append(line)
        else:
            parts.extend(re.findall(r"[^\d\s]+", line))

    instruction_names = {
        "NOP":       "No operation",
        "POP_TOP":   "Pop top item off stack",
        "ROT_TWO":   "Rotate items 2 places up the stack",
        "DUP_TOP":   "Duplicate top item on the stack",
        "ROT_THREE": "Rotate items 3 places up the stack",
        "RETURN_VALUE": "Return value from function",
    }

    try:
        for part in parts:
            if part != "END":
                instruction_name = instruction_names.get(part, "")

                if len(instruction_name) > 0:
                    print(
                        f"{label}{part:<16}",
                        f"{' ' * (len(instruction_name) - 1)}",
                        instruction_name.capitalize(),
                    )
    except UnicodeDecodeError:
        pass

    print("\n".join(comment_lines))


def _dis_print_labels(disassembly: str) -> None:
    lines = disassembly.strip().splitlines()
