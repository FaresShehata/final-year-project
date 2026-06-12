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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data["status"]),
            tags=data.get("tags"),
            metadata=data.get("metadata", {}),
        )


@dataclasses.dataclass(eq=False)
class Person:
    name: str = dataclasses.field(compare=False)
    age: int = dataclasses.field(compare=False)
    gender: str = dataclasses.field(compare=False)
    phone_numbers: list[str] = dataclasses.field(compare=False)
    address: Address = dataclasses.field(compare=False)
    email_addresses: list[str] = dataclasses.field(compare=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.age})"

    def __repr__(self) -> str:
        return f"<Person({self.name}, {self.age})>"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Person):
            raise NotImplementedError(f"Cannot compare a {type(self).__qualname__} "
                                      f"to an instance of type {o.__qualname__}")
        if not super().__eq__(o): return False
        return all(getattr(self, field) == getattr(o, field) for field in self.__annotations__ if field != "address")

    def __hash__(self) -> int:
        values = [getattr(self, field) for field in self.__annotations__]
        return hash(tuple(values))


@dataclasses.dataclass(slots=True)
class Address:
    street: str
    city: str
    country: str
    postal_code: str
    latitude: float = dataclasses.field(metadata={"tooltip": "degrees north"})
    longitude: float = dataclasses.field(metadata={"tooltip": "degrees east"})


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, slots=True)
class FrozenPoint:
    x: float
    y: float

    def distance(self, other: FrozenPoint) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


FrozenPerson = dataclasses.make_dataclass("FrozenPerson",
                                         [("name", str),
                                          ("age", int),
                                          ("gender", str),
                                          ("phone_numbers", list[str]),
                                          ("address", Address)],
                                         namespace={
                                             "__repr__": lambda self:
                                                 f"<{self.__class__.__qualname__}(name={self.name!r}, age={        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "locals":   frame.f_locals,
        "globals":  frame.f_globals,
        "constants": tuple(map(repr, frame.f_code.co_consts)),
        "filename": frame.f_code.co_filename,
        "lineno":   frame.f_lineno,
        "argcount": frame.f_code.co_argcount,
        "closures": tuple(closure.cell_contents for closure in frame.f_code.co_cellvars),
    }


def call_depth_probes() -> list[tuple[int, dict]]:
    frames: list[tuple[int, dict]] = []
    current_frame = sys._getframe()
    while True:
        try:
            d = caller_info(depth=len(frames))
            frames.append((len(frames), d))
        except ValueError:
            break
        current_frame = current_frame.f_back
    return frames[::-1]


def parsed_call_stack() -> list[inspect.FrameInfo]:
    frames = inspect.stack()[::-1][:-1]      # exclude __main__
    return [inspect.FrameInfo.fromframes(frame) for frame in frames]


# ── Garbage Collection ───────────────────────────────────────────────────────-

gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE |
             gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS |
             gc.DEBUG_SAVEALL | gc.DEBUG_STATS | gc.DEBUG_STATS | gc.DEBUG_TRACE)


# ── Tracing Memory Allocations ────────────────────────────────────────────────

tracemalloc.start(50)
snapshot = tracemalloc.take_snapshot()

for line in annotated_disassembly(hot_path(1_000)).splitlines():
    print(line.strip())
print("")

