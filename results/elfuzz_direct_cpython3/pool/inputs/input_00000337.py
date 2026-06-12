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
    x: int
    y: int
    z: int = 0
    name: str = ""


@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    height: float = 1.80
    weight: float = 79.3
    birthday: date = dataclasses.field(default_factory=date.today)
    alive: bool = True


# ── Slots ─────────────────────────────────────────────────────────────────────

#@dataclasses.dataclass(slots=True)
class Robot:
    model: str
    year: int
    speed: int = 100
    color: str = ""
    sensors: ClassVar[tuple] = ("rgb", "lidar") 
    coordinates: tuple[float, float]
    
    def drive(self, distance: float):
        if not self.is_alive():
            raise RuntimeError("Robot is dead.")
            
        if distance <= 0:
            raise ValueError("Distance must be positive.")
        
        self.coordinates = (self.coordinates[0] + distance * math.sin(math.radians(self.speed)),
                            self.coordinates[1] - distance * math.cos(math.radians(self.speed)))

    def is_alive(self) -> bool:
        return self.year < datetime.datetime.now().year


# ─── Structural Pattern Matching ───────────────────────────────────────────────

def match_nurse(nurse: Nurse) -> None:
    if isinstance(nurse, Doctor):
        print("Doctor")
    elif isinstance(nurse, Dentist):
        print("Dentist")


def match_person(person: PersonLike) -> None:
    match person:
        case {"name": name, "age": age}:
            print(f"Name: {name}, Age: {age}")
        case {"name": name, "age": age, **props}:
            print(f"Name: {name}, Age: {age}")
            for key, value in props.items():
                print(f"{key}: {value}")


def match_enum(status: Status):
    match status:
        case Status.PENDING:
            print("Pending")
        case Status.SUCCESS:
            print("Success")
        case _ as other_status:
            print(other_status.value)


def match_tuple(tuple_thingy: tuple[int, ...]):
    match tuple_thingy:
        case [first, second]:
            print(f"{first} and {second}")
        case [first, *rest]:
            print(first)

        self.status = Status.RUNNING
        try:
            result = asyncio.run(self.func())
        except BaseException as exc:
            self.status = Status.FAILED
            raise exc
        else:
            self.status = Status.SUCCESS
        finally:
            print(f"[{time.strftime('%H:%M:%S')}] Finished {self.name}")

def map_async(func: Callable[[str], Awaitable[str]], tasks: list[Task]) -> list[Awaitable[str]]:
    results = []
    for task in tasks:
        loop = asyncio.get_running_loop()
        future = asyncio.ensure_future(task.start(), loop=loop)
        results.append(asyncio.wrap_future(future))
    return asyncio.gather(*results)


