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


@runtime_checkable
class IterableWithIndex(Generic[K, V], Protocol):
    """
    A sequence-like protocol with an additional index attribute so we can iterate over the items in parallel.

    Note: This is an example only - there are better ways to do this.
    """

    def __iter__(self) -> Iterator[Tuple[V, K]]:
        ...

    def __getitem__(self, i: K) -> V:
        ...

    def __len__(self) -> int:
        ...

    @property
    def index(self) -> Sequence[int]:
        """Return the list of indices for each item."""
        return [i for i, _ in enumerate(self)]


def test_iter_with_index() -> None:
    class Foo(IterableWithIndex[int, str]):
        def __init__(self, items: Sequence[str]) -> None:
            self.items = items

        def __iter__(self) -> Iterator[Tuple[str, int]]:
            yield from zip(
                (item for item in self.items), range(len(self))
            )  # noqa: WPS317

        def __getitem__(self, key: int) -> str:
            return self.items[key]

        def __len__(self) -> int:
            return len(self.items)


async def main():
    await asyncio.gather(test_iter_with_index(), test_structural_pattern_matching())


# noinspection PyShadowingNames
async def test_structural_pattern_matching()-> None:

    def add(a: int | float, b: int | float) -> int | float:
        return a + b

    assert add(5.6, 4.5) == 10.1
    assert add(5, 4) == 9

    # Structural pattern matching
    def add(a: object, b: object) -> object:
        match (a, b):
            case (int | float, int | float):
                return a + b
            case (str, str):
                return f"{a} and {b}"
            case _:
                raise NotImplementedError(f"cannot handle type: ({type(a)}, {type(b)})")

    assert add(5.6, 4.5) == 10.1
    assert add(5, 4) == 9
    assert add("foo", "bar") == "foobar"

    try:
        print(add(5, True))  # type: ignore[unreachable]
    except NotImplementedError as e:
        print(e)


# noinspection PyShadowingNames
async def test_data_classes()-> None:
    @dataclasses.dataclass(slots=True)
    class Foo:
        x: int
        y: int

    foo_1 = Foo(x=3, y=4)
    foo_2 = Foo(y=4, x=3)

    print(foo_1.x)  # Access attributes by name
    print(foo_1.y)