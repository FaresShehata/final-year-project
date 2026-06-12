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
    from types import TracebackType


def _test_async_iter():
    """async generator yield with await expression"""
    async def test() -> None:
        for num in (await iter((1, 2))) * 3:
            print(num)

    assert [num for num in test()] == [1, 2] * 3
    assert [num for num in test()] == [1, 2] * 3
    assert [num for num in test()] == [1, 2] * 3
    assert [num for num in test()] == [1, 2] * 3
    assert [num for num in test()] == [1, 2] * 3


def _test_await():
    """Await an awaitable object"""
    async def test() -> str:
        return "hello"

    assert test().result() == "hello"
    assert asyncio.run(test()) == "hello"


class AsyncIterator(Protocol):
    async def __aiter__(self) -> AsyncIterator[T]:
        raise NotImplementedError()

    async def __anext__(self) -> T:
        raise NotImplementedError()


@runtime_checkable
class SupportsGreaterOrEqual(enum.Enum):
    @property
    def order(self) -> int:
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class Node:
    """Node class"""

    value: int = 42
    name: str | None = None
    children: list[Node] = dataclasses.field(default_factory=list)


@overload
def _test_structural_pattern_matching(x: int) -> bool:
    ...


@overload
def _test_structural_pattern_matching(x: float) -> bool:
    ...


@overload
def _test_structural_pattern_matching(x: str) -> bool:
    ...


# Structural Pattern Matching (SPM)
def _test_structural_pattern_matching(x: int | float | str):
    match x:
        case {}:
            return False
        case {} if not isinstance(x, dict):
            return False
        # case _dict if len(_dict) > 5:
        #     return True
        case {**rest} if len(rest) > 5:
            return True
        case _:
            return True


class MyError(Exception):
    pass


