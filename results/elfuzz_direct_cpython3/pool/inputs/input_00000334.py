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

    def update_status(self, new_status: Status) -> None:
        assert new_status.is_terminal(), "new status must be terminal"
        self.status = new_status
        self._history.append(new_status)

    @property
    def duration(self) -> float:
        if len(self._history) <= 1:
            return 0.0
        else:
            return self._history[-1].value - self._history[0].value

    def __repr__(self) -> str:
        return "<Task {} {}>".format(self.name, self.status.value)


# ── Types ─────────────────────────────────────────────────────────────────────

DictStrInt = dict[str, int]


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
    candidate = 3
    while True:
        if all(candidate % p != 0 for p in seen):
            yield candidate
            seen.add(candidate)
            candidate += 2
        else:
            candidate += 2


def permutations(iterable) -> Iterator[tuple]:
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
