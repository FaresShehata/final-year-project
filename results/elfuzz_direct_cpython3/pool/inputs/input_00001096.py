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
    LOW      = -1  # low priority
    NORMAL   = 0   # normal (default) priority
    HIGH     = 1   # high priority


@runtime_checkable
class Repr(Protocol[K]):
    @property
    def repr(self: K) -> str: ...


# ─── Classes ────────────────────────────────────────────────────────────────

# partial class demo
class Partial(Generic[T]):
    def __init__(self, func: Callable[[T], T]) -> None:
        self.func = func
    
    def __call__(self, *args: T.args, **kwargs: T.kwargs) -> T:
        return self.func(*args, **kwargs)


@dataclasses.dataclass
class Person:
    name: str
    age: int
    gender: str
    phone: str | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, age={self.age})"


# ─────── Helper Functions ────────────────────────────────────────────────────

def get_age_range(age: int) -> tuple[int, int]:
    if age < 30:
        return (0, 29)
    elif age >= 65:
        return (64, 100)
    else:
        return (age//10*10, age//10*10+9)

async def sleep(seconds: float):
    await asyncio.sleep(seconds)

async def wait_until(predicate: Callable[[], bool],
                     timeout: float = 1.0,
                     step: float = 0.05) -> float:
    while True:
        await sleep(step)
        if predicate():
            return timeout

async def run_asyncio(fut: asyncio.Future[None]):
    try:
        await fut
    except KeyboardInterrupt:
        print("^C received")

async def main() -> None:
    t_start = time.time()
    await asyncio.gather(
        echo("hello"),
        echo("world"),
        echo("hi"),
        echo("bye"),
    )
    t_stop = time.time()

    print(t_stop-t_start)

asyncio.run(main())

print("\n\n")


# ─────── Data Structures ────────────────────────────────────────────────────

# list demo
l0 = [random.randint(-10, 10) for _ in range(random.randint(3, 10))]
print(l0)
l0.append(7)
l0.sort()
print(l0)

l1 = []
for i in range(random.randint(3, 10)):
    l1.append(i*i)
print(l1)

l1.insert(0, 88)
print(l1)

tup = ("a", "b", "c")
print(len(tup))
print(tup.index('b'))
l2 = list(tup)
print(l2)
print(tuple(range(5)))
print(list(reversed(sorted(["hey", "ho", "lets go"], reverse=True))))
print((2, ) + (3, ))
print(("foo", ) * 3)

d