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
    async with AsyncContextManager() as cm:
        pass


# Example 3 - Async Stack
async def pop(stack: deque) -> Optional[str]:
    item = stack.popleft()
    await asyncio.sleep(1)
    print(item)
    return item


async def push(stack: deque, value: str):
    await asyncio.sleep(1)
    print(value)
    stack.appendleft(value)


async def example3():
    stack = deque(["one", "two"])
    await asyncio.gather(push(stack, "three"), pop(stack), pop(stack))


# Example 4 - Async Queue
async def producer(queue: asyncio.Queue) -> None:
    for i in range(5):
        await queue.put(random.randint(1, 10))
        await asyncio.sleep(1)


async def consumer(queue: asyncio.Queue, name: str) -> None:
    while True:
        value = await queue.get()
        print(f"{name} got {value}")
        await asyncio.sleep(random.randint(1, 3))
        queue.task_done()


async def example4():
    q = asyncio.Queue(maxsize=3)
    ptask = asyncio.create_task(producer(q))
    ctask1 = asyncio.create_task(consumer(q, "first"))
    ctask2 = asyncio.create_task(consumer(q, "second"))

    await q.join()

    await ptask
    await ctask1
    await ctask2


# Example 5 - Async Semaphore
async def task(semaphore):
    with (yield semaphore.acquire())


async def main():
    sem = asyncio.Semaphore(5)
    tasks = [asyncio.ensure_future(task(sem)) for _ in range(10)]
    await asyncio.wait(tasks)


# Example 6 - Async Lock
class TaskLock(asyncio.Lock):
    def __init__(self):
        super().__init__()
        self.counter = 0


async def acquire_lock(lock: TaskLock):
    async with lock:
        print("Acquired lock")


async def release_lock(lock: TaskLock):
    async with lock.locked():
        print("Released lock")


async def example6():
    lock = TaskLock()
    acq_task = asyncio.create_task(acquire_lock(lock))
    rel_task = asyncio.create_task(release_lock(lock))

    await acq_task
    await rel_task


# Example 7 - Async Condition
condition = asyncio.Condition()


async def wait(timeout: float