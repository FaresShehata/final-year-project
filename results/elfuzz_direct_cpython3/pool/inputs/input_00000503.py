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

    # comparison key ignores status and history
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Task): raise TypeError()
        return (self.priority.value, self.id) < (other.priority.value, other.id)

    @property
    def history(self) -> tuple[Status, ...]: return tuple(self._history)
    
    @history.setter
    def history(self, value: Iterable[Status]): self._history.clear(), self._history.extend(value)

    @overload
    def merge(self, task: Task) -> None: ...
    @overload
    def merge(self, tasks: list[Task]) -> None: ...
    
    def merge(self, tasks: Union[Task, list[Task]]) -> None:
        if isinstance(tasks, Task):
            tasks = [tasks]
            
        if len(tasks) == 0:
            raise ValueError("Cannot merge empty tasks.")
        
        merged_priority = max(task.priority for task in tasks)
        merged_tags = sorted(set.union(*(task.tags for task in tasks)))
        merged_metadata = {}
        for task in tasks:
            merged_metadata.update(task.metadata)
            merged_history = [*task.history]
            merged_history.reverse()
            self._history = merged_history
        
        self.priority = merged_priority
        self.tags = merged_tags
        self.metadata = merged_metadata


# ── Collections ───────────────────────────────────────────────────────────────-

@dataclasses.dataclass
class Statistics(Generic[K, V]):
    total: int = 0
    min_value: Optional[V] = None
    max_value: Optional[V] = None
    mean: Optional[float] = None
    median: Optional[V] = None
    values: List[V] = dataclasses.field(default_factory=list, init=False, hash=False, eq=False, compare=False)
    buckets: Dict[int, int] = dataclasses.field(default_factory=defaultdict(int), init=False, hash=False, eq=False, compare=False)

    def track(self, value: V) -> None:
        self.values.append(value)
        self.total += 1
        self.min_value = min([self.min_value or value, value])
        self.max_value = max([self.max_value or value, value])
        bucket_size = ceil(log(len(self.buckets)) / log(2))
        bucket_number = floor((value - min(self.buckets.keys())) // bucket_size)
        self.buckets[bucket_number] += 1
        self.mean = sum(self.values) / len(self.values)

    def update_median(self) -> None:
        s = sorted(self.values.copy())
        length = len(s)
        if length % 2 == 0:
            median_index =
# ── Utilities ─────────────────────────────────────────────────────────────────

def sleep_until(t: float) -> None:
    current_time = time.time()
    elapsed = t - current_time
    if elapsed > 0:
        time.sleep(elapsed)


async def wait_for_condition(condition: Callable[[], bool]) -> None:
    while not condition(): await asyncio.sleep(1)


async def calculate_pi(N: int) -> float:
    count_inside = 0
    for i in range(N):
        x = random.random()
        y = random.random()
        inside = x**2 + y**2 <= 1
        count_inside += int(inside)
    return 4 * count_inside / N


# ── Generators ────────────────────────────────────────────────────────────────

def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def odd_numbers() -> Generator[int, None, None]:
    n = 3
    while True:
        yield n
        n += 2


def primes() -> Generator[int, None, None]:
    yield 2
    seen = set()
