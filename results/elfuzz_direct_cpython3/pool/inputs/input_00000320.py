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


async def coro():
    pass


def sync_func(a: int) -> str:
    return str(a)


@overload  # Python >= 3.8
def overloaded() -> None:
    ...


@overload
def overloaded() -> bool:
    ...


def overloaded() -> bool:
    if True:
        return False
    else:
        return True


def main() -> None:
    print(unpack_header(b"foo\x00\0\0\0"))
    print(interleave_struct([(69.0, 74.0, 35.0)]))
    print(array_ops())
    print(sync_callables())


print(dataclasses_fields(Foo(bar=5)))


def sleep_and_print(n: int):
    print(f"sleeping {n} seconds")
    time.sleep(n)
    print(f"waking up after sleeping {n} seconds")


# ── generators ────────────────────────────────────────────────────────────────

def count_down(n: int):
    while n > 0:
        yield n
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

