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
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(**{**data, "priority": Priority(data["priority"]), "status": Status(data["status"])})


# ── Slots ─────────────────────────────────────────────────────────────────────

class ExampleClass:
    __slots__ = ["_value"]

    def __init__(self):
        self._value = ""

    def set_value(self, value: str) -> None:
        self._value = value

    def get_value(self) -> str:
        return self._value


# ── Structural pattern matching ───────────────────────────────────────────────

def match_obj(obj: V) -> K:
    match obj:
        case str():
            return obj.upper()

        case list() as items:
            return items[-1].upper()

        case _: raise ValueError(f"Unexpected value: {obj!r}")

    # unreachable code
    assert False, "Unreachable"


def match_list(lst: list[V]) -> K:
    match lst:
        case []:
            return []

        case [first, second]:
            return first + second

        case [head] | [head, tail] | [*rest]:
            return head

        case [] | [_]: raise ValueError("Expected at least one item")

    # unreachable code
    assert False, "Unreachable"


# ── Walrus operator ───────────────────────────────────────────────────────────

def sum_of_squares(numbers: list[int]) -> int:
    if numbers := iter(numbers):
        return sum(i**2 for i in numbers)


def delete_first_if(numbers: list[int], pred: Callable[[int], bool]):
    numbers.remove(next(filter(pred, numbers)))


# ── Generics ──────────────────────────────────────────────────────────────────

def convert_case(s: str, converter: Callable[[str], str]) -> str:
    return "".join(converter(c) for c in s)


def upper_camel_case(s: str) -> str:
    return convert_case(s, lambda c: c.lower())


def lower_snake_case(s: str) -> str:
    return convert_case(s, lambda c: "_" + c.lower())[:-1]


@overload
def parse_csv_line(line: str) -> tuple[list[str],from __future__ import annotations

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


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
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
