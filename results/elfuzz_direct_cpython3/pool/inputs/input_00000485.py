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
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> Task: ...


def task_runner(task: Task) -> Task:
    print(f"Running task {task.id}:", end=" ")
    for t in range(random.randint(3, 8)):
        print(".", end="", flush=True)
        await asyncio.sleep(random.random() / 10)
    if random.choice([True, False]):
        raise RuntimeError("Oops!")
    task.transition(Status.SUCCESS)
    print("done")
    return task


async def main() -> None:
    tasks: list[Task] = [
        Task(id=i, name=f"Task-{i}") for i in range(7)
    ]
    pending_tasks: list[Tuple[int, Task]] = []

    while True:
        num_pending = len(pending_tasks)
        for idx, task in reversed(sorted(tasks)):
            if task.is_terminal():
                continue
            elif not task.status.is_terminal():
                future = asyncio.ensure_future(
                    task.run(), loop=loop
                )
                task.transition(Status.RUNNING)
                pending_tasks.append((idx, task))
            else:
                task.transition(Status.SUCCEEDED)
                print(f"Succeeded: {task.name}")
        if num_pending == len(pending_tasks):
            break
        else:
            print(f"{len(pending_tasks)} tasks are running")

    await asyncio.wait([
        asyncio.create_task(task_runner(t)) for _, t in pending_tasks
    ])
    for t in sorted(tasks, key=lambda t: t.sort_key):
        print(t)


# ── Slots & __slots__ ─────────────────────────────────────────────────────────

print("\nSlots and __slots__")


class MyClass:
    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b

    def process(self) -> str:
        return f"{self.a}, {self.b}"

    def __repr__(self) -> str:
        return f"MyClass(a={self.a}, b={self.b})"


my_instance = MyClass(42, "Hello world!")

with open(__file__) as fp:
    source_code = "".join(fp.readlines())

print(my_instance.process())

with open(__file__) as fp:
    source_code_slots = "".join(fp.readlines())


class MyClassWithSlots(MyClass):
    __slots__ = ("a", "b", "c")

    def __init__(self, a: int, b: str, c: str) -> None:
        super().__init__(a=a, b=b)
        self.c = c

    def process(self) -> str:
        return f"{super().process()}, {self.c}"


my_instance_with_slots = MyClassWithSlots(42, "Hello world!", "This is the third field.")

with open(__file__) as fp:
    source_code_slots += "\n\nMyClassWithSlots:\n{0}".format(
        my_instance_with_slots.process()
    )

print(
    "{0}\n\n\n==\n\n\n".format(source_code),
    "\n\n\n",
    "{0}\n\n\n==\n\n\n".format(source_code_slots),
)

for line in source_code.splitlines():
    if line.startswith("class"):
        match = re.match(r"class (\w+)\