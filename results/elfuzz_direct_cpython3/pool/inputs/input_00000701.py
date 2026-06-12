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


# ── Data classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Item(Generic[K]):
    priority: int
    value: K

    # noinspection PyUnresolvedReferences
    def __repr__(self):
        return f"Item({self.priority=!r}, {self.value})"


@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    address: Address
    phone_numbers: tuple[str]
    email_address: str = dataclasses.field(default="none@example.com", compare=False)


@dataclasses.dataclass(frozen=True, slots=True)
class Address:
    street_name: str
    house_number: str | None = None


# ── Generic types ────────────────────────────────────────────────────────────

class Array[T]:
    def __init__(self, values: list[T] | None = None):
        if values is None:
            values = []
        self.values = values

    def append(self, item: T):
        self.values.append(item)

    def pop(self) -> T:
        return self.values.pop()

    def items(self) -> Iterator[T]:
        yield from self.values

    def count(self, item: T) -> int:
        return self.values.count(item)


class Factory[G]:
    def __init__(self):
        self.generation = 0

    def create(self) -> G:
        self.generation += 1
        return G(self.generation)


# ── Async/await ─────────────────────────────────────────────────────────────

async def sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def main() -> None:
    for _ in range(3):
        print(await get_random_number())
        await sleep(1.0)


async def get_random_number() -> float:
    return random.random()


asyncio.run(main())


# ── Protocols ───────────────────────────────────────────────────────────────

P = TypeVar("P")


@runtime_checkable
class Iterable(P):
    ...  # pragma: no cover

@runtime_checkable
class Container(P):
    ...  # pragma: no cover

@runtime_checkable
class Sized(P):
    def __len__(self) -> int: ...
    ...  # pragma: no cover

@runtime_checkable
class Reversible(P):
    ...  # pragma: no cover

@runtime

def process_count():
    with lock_for(Process):
        return multiprocessing.cpu_count()


_process_lock: Lock = Lock()

if TYPE_CHECKING:
    from subprocess import Process

else:

    # noinspection PyShadowingNames
    class Process(metaclass=ABCMeta):
        def terminate(self):
            pass

        @property
        def pid(self):
            ...

        @property
        def exitcode(self):
            ...

        def wait(timeout=None):
            ...

        def communicate(input=None, timeout=None):
            ...


try:
    from concurrent.futures import ThreadPoolExecutor as Executor

except ImportError:  # pragma: no cover

    # noinspection PyUnusedLocal
    class Executor(metaclass=ABCMeta):

        @abstractmethod
        def submit(func, *args, **kwargs):
            ...

        @abstractmethod
        def shutdown(wait=True):
            ...


class Event(Emitter[Event.EventData]):
    class EventData(Tuple[int, str]):
        pass


class Timer(EventTimer[Event.TimerEventData]):

    class TimerEventData(Event.EventData):
        def __new__(
                cls, interval, start_time, last_fire_time, next_fire_time, state, event_data
        ):
            instance = super().__new__(cls)
            instance.interval = interval
            instance.start_time = start_time
            instance.last_fire_time = last_fire_time
            instance.next_fire_time = next_fire_time
            instance.state = state
            instance.event_data = event_data
            return instance

        @classmethod
        def fire(cls, timer, current_time):
            return cls(
                current_time - timer.start_time + timer.last_fire_time,
                current_time,
                current_time - timer.start_time,
                current_time - timer.start_time + timer.last_fire_time,
                timer.state,
                timer.event_data,
            )


def test_timer_events():
    executor = Executor(max_workers=2)
    timer = Timer(executor, 2)
    timer.on_event(lambda t: print(t))
    timer.start()
    assert timer.is_running
    del timer
    executor.shutdown()


# ── Structural Pattern Matching ─────────────────────────────────────────────

def match_date(date: date.date):
    match date.year % 4:
        case 0:
            print("leap year!")
        case _:
            print("not a leap year :(")


match_date(datetime.date.fromisoformat("2023-09-17"))


def match_typed_dict(dct: dict[str, int]) -> None:
    match dct:
        case {"a": x}:
            print(x)
        case {"b": x}:
            print(x)
        case {"c": 1}:
            print("found c")
        case {"d"}:
            print("found d")
        case {"e": _, "f": 2}:
            print("found e and f")
        case _:
            print("unknown dict")


match_typed_dict({"a": 1})
match_typed_dict({"b": 2})
match_typed_dict({"c