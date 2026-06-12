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
    from collections.abc import Iterable, Sequence
    from typing_extensions import Self

    from .types import *
    from .utils import *


# ── Utilities ─────────────────────────────────────────────────────────────────

def is_empty(obj: object) -> bool:
    if obj is None or len(obj) == 0:
        return True
    elif hasattr(obj, "__getitem__"):
        try:
            obj.__getitem__(slice(None))
        except IndexError:
            return True
        else:
            return False
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return False  # text strings are iterable
    return True


def print_dict(d: dict[str, Any]) -> str:
    lines = []
    if d:
        items = sorted(d.items())
        max_key_len = max(map(len, map(str, d)))
        lines.append("{")
        for k, v in items:
            lines.append(
                f"    {k:{max_key_len}} : {v!r},"
            )  # !r forces repr(), including quotes around strings
        lines[-1] = lines[-1].rstrip(",")
        lines.append("}")
    return "\n".join(lines)


# ─── Seed 02 ───────


async def sleep_until(time: float | None = None) -> None:
    """Sleep until the given time.

    If no argument is provided, sleep until the next second boundary.
    """
    if time is None:
        time = (time := int(time)) + 1
    while time > time := time % 60:
        await asyncio.sleep(0.01)


class SleepUntil:
    """A context manager that sleeps until a specific time."""

    def __init__(
        self,
        seconds: float | None = None,
        minutes: float | None = None,
        hours: float | None = None,
    ):
        self.time = seconds * 60**2 + minutes * 60 + hours

    def __enter__(self) -> SleepUntil:
        asyncio.create_task(sleep_until(self.time), name="sleep_until")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass


# ─── Seed 03 ───────


@dataclasses.dataclass
class Person:
    first_name: str
    last_name: str
    age: int


persons: list[Person] = [
    {"first_name": "James", "last_name": "Bond", "age": 38},
    {"first_name": "Miss", "last_name": "Moneypenny", "age": 37},
    {"first_name": "Nicky", "last_name": "Hicks", "age": 45},
]

for person in persons:
    print(persons.index(person))


# ─── Seed 04 ───────


@runtime_checkable
class Comparable(Protocol):
    @property
    def value(self) -> int: ...


@overload
def get_n_largest(values: list[int], n: Literal[1]) -> int: ...
@overload
def get_n_largest(values: list[int], n: Literal[-1]) -> list[int]: ...
@overload
def get_n_largest(values: list[int], n: int) -> list[int]: ...
@overload
def get_n_largest(values: list[int], n: int, *, reverse: bool) -> list[int]: ...


def get_n_largest(values: list[int], n: int, *, reverse: bool = False) -> list[int]:
    return sorted(values)[-n:] if reverse else sorted(values)[:n]


print(get_n_largest([random.randint(-90_000, 90_000) for _ in range(10)], 1, reverse=True))

get_n_largest(
    values=[random.randint(-90_000, 90_000) for _ in range(10)],
    n=1,
    reverse=True,
)
get_n_largest(values=[random.randint(-90_000, 90_000) for _ in range(10)], n=-1)
get_n_largest(values=[random.randint(-90_000, 90_000) for _ in range(10)], n=2)
get_n_largest(values=[random.randint(-90_000, 90_000) for _ in range(10)], n=10)