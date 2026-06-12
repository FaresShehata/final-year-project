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


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    address: Address

    class Address:
        street: str
        city: City


@dataclasses.dataclass(frozen=False)
class Book:
    title: str
    author: Person


# ── Slots (and Pickling) ──────────────────────────────────────────────────────

class Record:
    __slots__ = ["name", "age"]
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def to_dict(self) -> dict[str, Any]: ...
    def from_dict(cls, d: dict): ...  # type: ignore[misc]


# ── Structual Pattern Matching ─────────────────────────────────────────────────

class Shape(Generic[T]):
    def area(self) -> T:
        raise NotImplementedError()

    def perimeter(self) -> T:
        raise NotImplementedError()


class Polygon(Shape[int]):
    def __init__(self, sides: tuple[float, ...]) -> None:
        self.sides = sides

    def area(self) -> int: ...
    def perimeter(self) -> int: ...


class Circle(Shape[float]):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float: ...
    def perimeter(self) -> float: ...


shapes = [
    Polygon((3.4, 3.6)),
    Circle(8),
]

for shape in shapes:
    match shape:
        case Polygon(sides=side_lens) as p if sum(side_lens) == 180 and all(side > 0 for side in side_lens):
            print(p)
        case _:
            print("Not a valid polygon")


# ── Walrus Operator ───────────────────────────────────────────────────────────

def get_user_info(users: list[dict[str, str]], username: str) -> dict[str, str] | None:
    user = next(filter(lambda u: u["username"] == username, users), None)
    if user is None:
        return None

    user_id = user["id"]

    return {"user": user, "user_id": user_id}

users = [{"username": "alice", "email": "alice@example.com"}]

info = get_user_info(users, "alice") or {}
print(info["user"]["email"])

while info := get_user_info(users, "alice"):
    print(info["user"]["email"])
else:
    print("User not found.")


# ── Generics ─────────────────────────────────    """Auto-curry a function based on its arity."""
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

    def __init__(self, fn: Callable, *args):
        self.fn = fn
        self.args = args

    def run(self) -> Any:
        while isinstance(self.fn, Thunk):
            self.fn = self.fn.run()
        fn = self.fn
        args = self.args
        del self.fn, self.args
        return fn(*args)


def trampoline(coroutine: Callable[..., Generator]) -> Callable[..., Any]:
    """Trampoline a coroutine."""

    def trampolinized(*args, **kwargs):
        gc = coroutine(*args, **kwargs)
        while True:
            try:
                value = next(gc)
            except StopIteration as exc:
                return exc.value
            else:
                gc = Thunk(value, value)
    return trampolinized


