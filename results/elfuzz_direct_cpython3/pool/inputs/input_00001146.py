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
    FINISHED  = "finished"


@runtime_checkable
class AsyncIterator(Protocol[K]):
    """Async iterable protocol."""

    def __aiter__(self) -> AsyncIterator[K]:
        ...

    async def __anext__(self) -> K | None:
        ...


# ── Data classes ────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    height: float
    weight: float


# ── Slots ───────────────────────────────────────────────────────────────────

class SlotPerson:
    __slots__ = ["name", "age"]

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

# ── Structural pattern matching ──────────────────────────────────────────────

x = 1 + 2j  # complex numbers are always real and imaginary parts non-zero

if isinstance(x, complex):  # check class type
    print("complex number")
elif isinstance(x, int):  # check integer type
    print("integer")
else:  # check both class and integer types
    print("not a complex or integer")


match x:
    case 1 + 2j:
        print("complex number")
    case _:
        print("not a complex or integer")


a = 1
b = 2
c = 3
match [a, b, c]:
    case [_, _, _] if len(set([a, b, c])) == 2:
        print("all distinct")
    case [_, _, _] if sum(filter(lambda n: n < 2, [a, b, c])) > 0:
        print("some negative")
    case _:
        print("invalid combination")

# ── Walrus operator ────────────────────────────────────────────────────────

while (n := input()) != 'quit':
    # do stuff...

# ── Generics ────────────────────────────────────────────────────────────────

def take_n_items(n: int, items: Iterable[T]) -> list[T]:
    taken = []
    for item in items:
        taken.append(item)
        if len(taken) >= n:
            break
    return taken


async def take_n_items_async_iter(
    n: int, items: AsyncIterable[T]
)        args = (*args, b2)
    if c3 is not None:
        args = (*args, c3)
    if d4 is not None:
        args = (*args, d4)
    if e5 is not None:
        args = (*args, e5)
    if f6 is not None:
        args = (*args, f6)
    if g7 is not None:
        args = (*args        merged_args = {**kwargs, **dict(zip(kwargs.keys(), other_args))}

        # Call the original function with the merged args
        return func(**merged_args)

    return wrapped


add5 = partial(add3, c=5)


# ── Trampoline pattern ──────────────────────────────────────────────────────

def trampoline(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        while True:
            try:
                res = fn(*args, **kwargs)
            except StopIteration as e:
                return e.value
            else:
                args = ()
                kwargs.clear()
                if isinstance(res, tuple):
                    fn, args, kwargs = res
                elif isinstance(res, list):
                    fn, *res = res
                    args += res
                elif callable(res):
                    fn = res
            finally:
                pass
    return wrapped


# ── Comprehensions, generators, iterators, etc. ────────────────────────────

nums = [
    i for i in range(10_000)
]

even_numbers = (
    i for i in nums
    if not i % 2
)

square_nums = (
    num ** 2 for num in nums
)

pairs = (
    (num, num ** 2) for num in nums
)

doubles = {
