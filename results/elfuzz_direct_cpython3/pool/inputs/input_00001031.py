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

    def mark_as_completed(self, result: T = "") -> None:
        self._history.append(Status.SUCCESS)
        self.status = Status.SUCCESS
        self.metadata["result"] = result

    def mark_as_failed(self) -> None:
        self._history.append(Status.FAILED)
        self.status = Status.FAILED

    def mark_as_cancelled(self) -> None:
        self._history.append(Status.CANCELLED)
        self.status = Status.CANCELLED

    @property
    def history(self) -> tuple[Status]:
        return tuple(self._history)


def random_delay(min_seconds: float = 0.1, max_seconds: float = 0.5) -> float:
    """Generates a random delay between min and max seconds."""
    return random.uniform(min_seconds, max_seconds)


@dataclasses.dataclass(slots=True)
class PointDataClass:
    x: float
    y: float

    def distance(self, other: PointDataClass) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))


# ── Slots =====================================================================

class Slotter(Generic[K, V]):
    __slots__: ClassVar[list[str]] = []

    def __init__(self, key: K, value: V) -> None:
        super().__setattr__("key", key)
        super().__setattr__("value", value)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}({self.key}, {self.value})>"

    def __hash__(self) -> int:
        return hash((self.key, self.value))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Slotter) \
            and self.key == o.key \
            and self.value == o.value

    def __getattribute__(self, __name: str) -> Any:
        if __name not in ("__slots__"):
            return getattr(self.value, __name)
        return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name not in ("__slots__"):
            setattr(self.value, __name, __value)
        else:
            super().__setattr__(__name, __value)


# Walrus Operator ============================================================

my_list = ["this is a string"]
int(my_list[0]) if len(my_list) > 0 else None

# Structural Pattern Matching ================================================

match point_data_class:
    case PointDataClass(x, _):  print(f'x={x}')
    case _:                     print('Unknown point')

# Generics =========================================================================

T           = TypeVar("T")
Container[T] = Generic[T]


class Queue(Container[T]):
    pass


queue :Queue[int]
queue.append(1)
queue.append(2)
queue.append(3)

for item in queue:
    print(item)


# Exception Groups ==============================================================

try:
    raise ValueError("Oopsie!")
except Exception:
    raise ValueError("Boom!") from Exception()

ex_group = ExceptionGroup(
    f"Multiple exceptions",
    [ValueError(), ZeroDivisionError()]
)

print_type(object())


async def main():
    task_1 = asyncio.create_task(simple_coroutine())
    await asyncio.sleep(0.5)
    task_2 = asyncio.create_task(coroutine_with_args('a', 'b'))
    # TODO - change the sleep time so we can see what happens after awaiting on `task_1`
    await asyncio.wait([task_1, task_2])
    # TODO - wait until both tasks are done before exiting the program


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    finally:
        loop.close()