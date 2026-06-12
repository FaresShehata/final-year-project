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

except ImportError:
    from threading import ThreadPoolExecutor  # type: ignore[assignment]

    class Executor(ThreadPoolExecutor):
        @staticmethod
        def shutdown(*args, **kwargs):  pass


# ── Sequence protocols ────────────────────────────────────────────────────────

@overload
def reverse(lst: List[int]) -> List[int]: ...
@overload
def reverse(lst: Tuple[int]) -> Tuple[int]: ...

def reverse(lst: Sequence[int]) -> Sequence[int]:
    """Reverse the input sequence."""
    reversed_lst = lst[::-1]
    assert isinstance(reversed_lst, type(lst))
    return reversed_lst


assert reverse([1, 2, 3, 4]) == [4, 3, 2, 1]


# ── Context managers ──────────────────────────────────────────────────────────

class ContextManager:
    def __enter__(self) -> object:
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        ...


with open('file.txt', mode='w') as file:
    file.write('Hello World')


# ── Generators ───────────────────────────────────────────────────────────────

def fibonacci(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    while n > 0:
        yield a
        a, b = b, a + b
        n -= 1


fibonacci_generator = fibonacci(5)

next(fibonacci_generator)  # 0
next(fibonacci_generator)  # 1
next(fibonacci_generator)  # 1
next(fibonacci_generator)  # 2
next(fibonacci_generator)  # 3
next(fibonacci_generator)  # StopIteration


# ── Async context managers ────────────────────────────────────────────────────

async def run_async_context_manager(context_manager: CoroutineContextManager) -> None:
    async with context_manager as result:
        assert isinstance(result, ResultType)


@contextmanager  # type: ignore[misc]
async def some_coroutine_context_manager() -> Iterator[ResultType]:
    # coroutine code here...
    ...


run_async_context_manager(some_coroutine_context_manager())

# ── Structural Pattern Matching ──────────────────────────────────────────────

match 1:
    case 1:
        print("one")
    case 2:
        print("two")
    case 3 |        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(pred(succ(
        pred(succ(pred(succ(pred(succ(pred(succ
    def overlap(self, other: Span) -> int:
        return max((self.end, other.end) - min((self.start, other.start)))


# ── Text formatting ───────────────────────────────────────────────────────────

class Formatter(string.Formatter):
    def format_field(self, value, spec):
        try:
            return super().format_field(value, spec)
        except (TypeError, AttributeError):
            return repr(value)


print(Formatter().vformat("{a} {b}", [], {"a": 3.14, "b": "π"}))


# ── String tokenization ───────────────────────────────────────────────────────

input_string = 'Hello world'
tokens = list(tokenize.generate_tokens(io.StringIO(input_string).readline))

for token in tokens:
