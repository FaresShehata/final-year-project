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


class Mode(enum.IntFlag):
    READ    = 0b001
    WRITE   = 0b010
    EXECUTE = 0b100
    ALL     = READ | WRITE | EXECUTE


class Direction(enum.Enum):
    LEFT  = "<"
    RIGHT = ">"


# ── Data classes ──────────────────────────────────────────────────────────────

@d
class Point:
    x: int
    y: int

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


Point_t = dataclasses.dataclass(
    field_dunders=False,
    frozen=True,
    order=True,
    slots=True,
    repr=True,
    eq=True,
    unsafe_hash=True,
    kw_only=False,
    init_fields_order="xy",
    fields_init_order=("x", "y"),
    ordered=True,
    hash_code=None,
    init=False,
    repr_name="__main__.Point",
    match_args=True,
    match_names=True,
    config=dataclasses.Config(),
)

@d
class Person:
    name: str
    age: int


Person_t = dataclasses.dataclass(
    field_dunders=False,
    frozen=True,
    order=True,
    slots=True,
    repr=True,
    eq=True,
    unsafe_hash=True,
    kw_only=False,
    init_fields_order="name_age",
    fields_init_order=("name", "age"),
    ordered=True,
    hash_code=None,
    init=False,
    repr_name="__main__.Person",
    match_args=True,
    match_names=True,
    config=dataclasses.Config(),
)


# ── Generics ──────────────────────────────────────────────────────────────────

# @runtime_checkable
# class Hashable(Protocol[K]):
#     def __hash__(self) -> int:
#         ...


@runtime_checkable
class Hashable(Protocol[K]): ...
_T = TypeVar("_T")


class Hashable(Generic[_T]):
    @overload
    def __hash__(self) -> int:
        ...           # pragma: no cover
    
    @overload
    def __hash__(self: Hashable[T]) -> Hashable[int]: ...
    

class MyHashable(Hashable[str]):
    def __init__(self, s: str):
        self.s = s

    def __hash__(self) -> int:
        return hash(self.s)

    def __eq__(self, other):
        returnNOT   = lambda p: p(FALSE)(TRUE)

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


