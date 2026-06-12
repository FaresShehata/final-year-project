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
    Iterable,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from typing_extensions import Self


"""
async/await
"""


class Future:
    pass


@dataclasses.dataclass(frozen=True)
class TaskState(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value


def sleep(seconds: float) -> Future:
    """
    A simple blocking function that will wait for a given amount of seconds.
    """
    start_time = time.time()
    while True:
        if time.time() - start_time >= seconds:
            break
    return None


async def async_sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


# TODO: Add more examples on future and tasks with cancellation.
#       Add more examples on asyncio task scheduler.


######################################################################
# PROTOCOLS
######################################################################

T = TypeVar("T")


class Comparable(Protocol[T]):
    def __lt__(self, other: T) -> bool: ...


# This is just an example, in real-world code you should use type annotations instead.
class Node(Generic[T], Comparable[T]):
    value: T
    next: Node[T] | None

    def __init__(
        self, value: T, next_node: Node[T] | None = None
    ) -> None:
        self.value = value
        self.next = next_node or None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value})"


def insert(node: Node[T]) -> None:
    global head
    # TODO: Handle the case where node's value is already present in the list.
    if not head:
        head = node
        return

    current_node = head
    previous_node = None
    while current_node:
        if node < current_node:
            if previous_node:
                previous_node.next = node
                node.next = current_node
            else:
                head = node
                node.next = current_node
            break
        previous_node = current_node
        current_node = current_node.next


head: Node[int] = None
for i in range(15):
    node = Node(i)
    insert