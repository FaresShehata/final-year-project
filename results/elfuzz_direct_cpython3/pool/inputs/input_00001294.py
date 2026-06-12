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
    async def run(self) -> Result[T]: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Person:
    first_name: str
    last_name: str
    age: int

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotPerson:
    first_name: str
    last_name: str
    age: int

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


# ── Structural Pattern Matching ───────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Message:
    text: str

    @staticmethod
    def parse(text: str) -> Message:
        return Message(text=text.strip())

    def reply_with(self, new_text: str) -> Message:
        return Message(text=f'You said "{new_text}"')


console = RichConsole()

@console.command()
def hello(name: str):
    message = Message.parse(input('Say something > '))
    message.reply_with(message.text.upper())

hello(hide_output=True)


# ── Walrus Operator ───────────────────────────────────────────────────────────

choice: str = input("Enter a choice > ")
while (key := input("Enter a key > ")) == "":
    print(key + " is empty")


# ── Generics ─────────────────────────────────────────────────────────────────-

async def work(n: int) -> int:
    await asyncio.sleep(random.random())
    return n * n


async def main():
    start_time = time.perf_counter()
    tasks = [
        work(i).add_done_callback(
            lambda fut: console.print(f'{i}: {fut.result():,}')
        )
        for i in range(9_999)
    ]
    await asyncio.gather(*tasks)
    elapsed_seconds = time.perf_counter() - start_time
    console.print(f'Time: {elapsed_seconds:.3f}s')

    messages = ['a', 'b', 'c']
    console.print([message.capitalize() for message in messages])
    console.print({message.title().swapcase() for message in messages})
    console.print(tuple(message.swapcase() for message in messages))


asyncio.run(main())


# ── Exception Groups ──────────────────────────────────────────────────────────
#
# The `ExceptionGroup` class is designed to make it easier to handle multiple
# exceptions at once, especially when dealing with asynchronous code or other
# scenarios where you might have multiple paths leading to different kinds of
# exceptions. By grouping these exceptions together, you can provide a more
# comprehensive view of what went wrong and potentially take some action based on
# the nature of all the exceptions combined.

async def divide(a: int, b: int) -> tuple[float, float]:
    try:
        result_a: float = a / b
    except ZeroDivisionError as err:
        raise ZeroDivisionError("Cannot divide by zero") from err
    return a, result_a

async def factorial(number: int) -> int:
    if number <= 1:
        return 1
    else:
        result = await factorial(number-1)
        return number * result

async def main():
    numbers = [4, 8, 3, 6]
    results = []
    for num in numbers:
        loop = asyncio.get_running_loop()
        result = loop.create_task(factorial(num))
        results.append(result)

    group = asyncio.wait_for(asyncio.gather(*T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)
        
    def __delete__(self, obj):
        delattr(obj, self.priv)


def NonEmptyString() -> Annotated[str, Predicate(lambda s: len(s) > 0)]:
    return Annotated[str, Predicate(len)]

def PositiveNumber() -> Annotated[int, Predicate(lambda n: n >= 1)]:
    return Annotated[int, Predicate(int)]

def NonZeroInteger() -> Annotated[int, Predicate(lambda n: n != 0)]:
    return Annotated[int, Predicate(lambda n: n != 0)]

NonEmptyName:         Annotated[str, Predicate(len)]
PositiveNumberOfThreads: Annotated[int, Predicate(lambda n: n >= 1)]
PositiveNumberOfProcesses: Annotated[int, Predicate(lambda n: n >= 1)]


# ── Queueable ────────────────────────────────────────────────────────────────

class Queueable(Generic[T]):
    def __init__(self, items: Iterable[T]) -> None:
        self._queue = queue.Queue()
        for item in items:
            self.push(item)

    @property
    def empty(self) -> bool:
        return self._queue.empty()

    def push(self, item: T) -> None:
        self._queue.put(item)

    def pop(self) -> T:
        return self._queue.get()


class CancellableQueue(Queueable[P]):
    """A cancellable version of Queueable.

    This implementation differs from the standard library's `queue.Queue`
    by adding support for cancelation.
    
    The `push` method accepts an optional cancellation token which can be used
    to interrupt the process of pushing the given item onto the queue. If the
