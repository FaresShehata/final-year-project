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
    Dict,
    Generic,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from collections.abc import Generator


class State(enum.Enum):
    """States of a game."""

    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclasses.dataclass(frozen=True)
class GameEvent(NamedTuple):
    """Game events."""

    state: State


def get_events() -> Generator[GameEvent, None, None]:
    """Generate game events."""
    while True:
        yield GameEvent(state=State.RUNNING)
        yield GameEvent(state=State.PAUSED)


def run_game(events: Iterable[GameEvent]):
    """Run the game based on given events."""
    for event in events:
        print(event.state)
        if event.state == State.FINISHED:
            break


# Example 1 - Async Iterator
class AsyncIterator:
    def __init__(self, values: List[int]):
        self.values = iter(values)

    async def __aiter__(self) -> AsyncIterator:
        return self

    async def __anext__(self) -> int:
        try:
            return next(self.values)
        except StopIteration:
            raise StopAsyncIteration


async def example1():
    ai = AsyncIterator([5, 4, 3, 2, 1])
    async for i in ai:
        await asyncio.sleep(1)
        print(i)


# Example 2 - Async Context Manager
class AsyncContextManager:
    async def __aenter__(self) -> AsyncContextManager:
        print("Entering context manager")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        print("Exiting context manager")
        return False


async def example2():
    async with AsyncContextManager():
        await asyncio.sleep(1)
        print("Inside context manager")


# Example 3 - Coroutine
async def example3():
    print("Starting coroutine")

    # Get a reference to another coroutine.
    task = asyncio.create_task(example3_())

    # Wait for the other coroutine and its future tasks.
    done, pending = await asyncio.wait(
        [task, asyncio.current_task()], return_when=asyncio.ALL_COMPLETED
    )

