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


@dataclasses.dataclass(frozen=True)
class Foo:
    bar: int
    baz: str


def dataclass_demo():
    foo = dataclasses.make_dataclass(
        "Foo", [("bar", int), ("baz", str)], frozen=False, slots=True
    )
    assert isinstance(foo.bar, int)
    assert isinstance(foo.baz, str)


# ── protocols ─────────────────────────────────────────────────────────────────

T = TypeVar("T")


class Comparable(Protocol[T]):
    def __lt__(self, other: T) -> bool:
        ...  # checks if self < other


def compare(a: Comparable[V], b: V) -> bool:
    return a < b


# ── dataclasses ────────────────────────────────────────────────────────────────
#
# https://docs.python.org/3/library/dataclasses.html
#

# @dataclass(frozen=True, repr=False)


def dataclass_repr(d: Foo):
    return d.__repr__() == "<foo(bar=42, baz='abc')>"


# ── slots  ────────────────────────────────────────────────────────────────────


# @dataclass(slots=True)


def dataclass_slots(d: Foo):
    return True


# ── structrual pattern matching ────────────────────────────────────────────────


def match_int(i: int) -> str:
    match i:
        case 0:
            raise ValueError
        case -i:
            return f"negative {abs(i)}"
        case _:
            return f"positive {i}"


match_int(-3)  # raises ValueError
match_int(9)   # positive 9

a: int = 9
b: int = a
c: int = 10
d: str = "hello"
e: str = "world"

if c > b and d != e:
    print("ok")

# ── walrus ────────────────────────────────────────────────────────────────────


async def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return await fib(n - 1) + await fib(n - 2)


async def main():
    start = time.perf_counter()
    end = start + 60.0
    results = []
    while time.perf_counter() < end:
        results.append(await fib(random.randint(8, 20)))
    elapsed = time.perf_counter() - start
    print(results[:10])
        n -= 1


def generator_expression() -> Generator[int]:
    return (n + 1 for n in range(10))


@overload
def consume(gen: Iterable[object]) -> None:
    ...


@overload
def consume(gen: Iterator[object]) -> object | None:
    ...


def consume(gen):  # type: ignore[misc]  # returns different things depending on whether it's an iterator or not
    try:
        return next(gen)
    except StopIteration as e:
        return e.value


def stream(func: Callable[..., Generator], /, *args):
    gen = func(*args)
    result = consume(gen)
    while result is not None:
        print(result)
        result = consume(gen)


stream(count_down, 5)  # prints from 5 down to 0
stream(generator_expression)  # prints the values yielded by the generator expression


# ── more generators ───────────────────────────────────────────────────────────

def count_up_to(n: int) -> Generator[int, None, None]:  # generators can also have a final value
    i = 0
    while i < n:
        yield i
        i += 1


def count_down_to(n: int) -> Generator[int, None, None]:  # generatorsdef unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

