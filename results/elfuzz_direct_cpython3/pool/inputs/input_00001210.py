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
class AsyncIterable(Protocol[K], Iterable[K]):
    async def __aiter__(self) -> AsyncIterator[K]: ...


async def _next(iterable: AsyncIterable[K]) -> K:
    async for x in iterable:
        return x


async def next_or_none(iterable: AsyncIterable[K]) -> K | None:
    try:
        return await _next(iterable)
    except StopAsyncIteration:
        return None


async def first(iterable: AsyncIterable[K]) -> K:
    return await _next(iterable)


def run_coroutines(coros: list[Awaitable[T]]) -> tuple[tuple[None, T], ...]:
    """
    Run a number of coroutines concurrently, returning results as a tuple.
        
        Notes
        -----
        This function does not wait until *all* coroutines have been completed before 
        returning. It simply returns as soon as one coro has finished. If you need to 
        do something after each coroutine completes, consider using the *asyncio.gather*
        function instead.
    """
    done = []

    coroutines = [
        asyncio.create_task(coro)
        for coro in coros
    ]

    while coroutines:
        done.append((coroutines.pop(), await coroutines[-1]))
        while done and done[-1][1] is not None:
            yield done.pop()[1]
            coroutines.remove(done[-1])


# ─── Data Classes ─────────────────────────────────────────────────────────────


@dataclasses.dataclass(order=True)
class Person:
    id_: int = dataclasses.field(compare=False)
    name: str
    age: int = 999

    def __post_init__(self):
        self.id_ += 1


class PersonProto(dataclasses.dataclass):
    id_: int = dataclasses.field(default_factory=lambda: random.randint(0, 10**6))
    name: str
    age: int = 999

    def __hash__(self) -> int:
        return hash(self.id_)
    
    def __str__(self) -> str:
        return f"<id={self.id_}> {self.name!r} ({self.age})"


@dataclasses.dataclass(slots=True)
class Book:
    title: str
    author: str
    year_published: int
    year_first_printed: int = dataclasses.field(init=False)

    @property
    def year_first_printed(self) -> int:
        return max(
            self.year_published, 
            self.year_first_printed
        )

    def publish(self, year: int) -> None:
        self.year_first_printed = year


# ─── Generics ─────────────────────────────────────────────────────────────────


class Stack(Generic[T]):
    stack: list[T]

    def __init__(self):
        self.stack = []
    
    def push(self, item: T) -> None:
        self.stack.insert(0, item)
    
    def pop(self) -> T:
        return self.stack.pop(0)

    def peek(self) -> T:
        return self.stack[0]


# ─── Lists, Dictionaries, Sets ─────────────────────────────────import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
            raise ValueError(f"{value} out of bounds [{self.lo}, {self.hi}]")
        
        setattr(instance, self.name, value)

    def __get__(self, instance: T, owner: type[T]) -> Any:
        return getattr(instance, self.name)


# ─── INHERITANCE, SUBCLASSES AND SLOTS ───────────────────────────────────────


class BaseClassA(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: type[BaseClassA]) -> bool: 
        print(f"subclasshook() called with class {subclass.__name__}")
        return NotImplemented
    
    @property
    def val(self):
        return "V1"

class BaseClassB(BaseClassA): pass

print(issubclass(BaseClassB, BaseClassA)) # True


# ──────── 𝗖𝗢𝗥𝗡𝗜𝗧𝗔𝗧𝗜𝗢𝗡 𝘈porto 𝗛𝗲𝗿𝗲 𝗕𝗶𝗻𝗴 𝗠𝗮 𝗰𝗮𝗻 𝗶𝗻𝘁𝗲𝗿𝗽𝗿𝗼𝘀𝘀𝗼𝗿 𝗦𝘂𝗽𝗽𝗼𝗿𝗲𝗱 𝘁𝗵𝗲𝗿𝗲 𝘄𝗶𝗹𝗹 ᴜ𝘀𝗲 𝗼𝗻 𝘆𝗼𝘂𝗿 𝗥𝗲𝘅 tʜ ____h 𝗮𝗻𝗱 𝗳𝘆 𝗩 𝗹𝗲𝗿𝗲.
@functools.total_ordering
class MyNumber(int):
    def __eq__(self, other: int | float) -> bool:
        return super().__eq__(other)
    
    def __lt__(self, other: int | float) -> bool:
        return super().__lt__(other)
    

n1 = MyNumber(42)
assert n1 >= n1 - 1, f"{n1} should be greater than or equal to {n1-1}"
assert n1 <= n1 + 1, f"{n1} should be less than or equal to {n1+1}"

# ─── TYPES, MIRACULOUSLY ─────────────────────────────────────────────────────


def get_class_attributes(cls: type[object]) -> tuple[str]:
    """
    Get all attributes of the given class, including those inherited from its parents.
    """

    attrs = set(dir(cls))
    for parent in cls.mro():
        attrs.update(getattr(parent, "__dict__", {}))

    return tuple(attrs)


class MyClass:

    attr_1 = 1
    attr_2 = "a string"
    attr_3 = [1, 2]

    def method_1(self):
        pass


attrs = get_class_attributes(MyClass)
print(*sorted(attrs), sep="\n")


# ─── METACLASSES ──────────────────────────────────────────────────────────────


class Meta(type):

    def __new__(
        mcs,
        name: str,
        bases: tuple[type],
        namespace: dict[str, Any]
    ) -> type:
        assert "_meta_"