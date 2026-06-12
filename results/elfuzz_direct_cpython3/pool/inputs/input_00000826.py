"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def partially_apply_2(fn: Callable[[A], B], arg: A) -> Callable[[B], B]:
    """Partially apply the first argument of a binary function."""
    return lambda b: fn(arg, b)


add4 = curry(add3)(4)


# ── Partial application with arguments passed by value ─────────────────────────

def partial(fn: Callable[..., A], /, *args: A) -> Callable[..., A]:
    """Partial application by passing positional args as keyword-only args."""

    @functools.wraps(fn)
    def wrapper(*kwargs: Any) -> A:
        return fn(*(list(args) + [v for k, v in kwargs.items()]))
    return wrapper


@partial
def mul4(a: int, b: int, c: int) -> int:
    return a * b * c


mul4_by_value = partial(mul4, 4)


# ── Trampoline pattern ───────────────────────────────────────────────────────

coroutine_stack_size = 64
sys.setrecursionlimit(coroutine_stack_size**2)

async def coroutine_stack_test() -> None:
    loop = asyncio.get_event_loop()

    await asyncio.sleep(0)
    print(loop.stack_size())


# ── Async iterator protocol ───────────────────────────────────────────────────

class AsyncIterator(AsyncIterable[A]): 
    """An asynchronous iterable that wraps an asynchronous iterator.

    An implementation must provide both `aiter` and `anext`, or a TypeError will be raised.
    """

    @overload
    async def __aiter__(self) -> AsyncIterator[A]: ...

    @overload
    async def __anext__(self) -> A: ...

    async def __anext__(self): ... 


def async_iterator(iterable: Iterator[A]) -> AsyncIterator[A]:
    """Converts an asynchronous iterator into an asynchronous iterable.

    If the input iterator does not support `aiter`, this method returns a synchronous
    iterator instead.
    """

    class AsyncIteratorWrapper(AsyncIterator[A]):
        def __init__(self, iterable: Iterator[A]):
            self._iterable = iterable
            self._result   = next(iterable, None)
            self._done     = False

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.close()

        async def __ait"""

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
        self.sort_key = hash(tuple(sorted(self.tags)))

    def update_status(self, status: Status) -> None:
        if status.is_terminal():
            while len(self._history) > 0 and not self._history[-1].is_terminal():
                del self._history[-1]
            
            self._history.append(status)

        assert len(self._history) <= 3
        
        if status == Status.RUNNING:
            self.status = Status.RUNNING
        elif status == Status.SUCCESS:
            self.status = Status.SUCCESS
        else:
            raise ValueError(f"Invalid status: {status}")

    @property
    def history(self) -> list[Status]:
        return [*self._history]

    def merge(self, other: Task) -> Task:
        task = Task(
            id       = self.id,
            name     = self.name,
            priority = min(self.priority, other.priority),
            status   = self.status,
            tags     = sorted(set(list(self.tags) + list(other.tags))),
            metadata = {},
        )

        task.update_status(Status.SUCCESS)
        return task


def add_tags(task: Task, *tags: str) -> Task:
    task.tags.extend(tags)
    task.sort_key = hash(tuple(sorted(task.tags)))
    return task


def merge_tasks(tasks: list[Task]) -> Task:
    tasks.sort(key=lambda t: t.priority)
    
    res = tasks.pop(0).merge(tasks.pop(0))
    for task in tasks:
        res.merge(task)

    return res


# ── Generics ──────────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)


class AbstractCollection(Generic[T_co]):
    async def add(self, item: T_co) -> None: ...
    async def pop(self) -> T_co: ...
    

