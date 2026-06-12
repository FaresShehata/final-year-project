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

# ── Classes and Interfaces ───────────────────────────────────────────────────


@runtime_checkable
class HasStatus(Protocol[K]):
    status: Status

@dataclasses.dataclass(init=False)  # default values not allowed
class AsyncQueue(Generic[T]):
    queue: list[T]
    maxsize: int | None = None
    _qsize: int = dataclasses.field(default=0)
    
    def __init__(self, items: Iterable[T] | None=None, *, maxsize: int | None=None):
        self.maxsize = maxsize
        if isinstance(items, (list, tuple)):
            self.queue = list(items)
        else:
            self.queue = []
        
        if len(self.queue) > self.maxsize:
            raise ValueError(f"Max size exceeded: {len(self)} > {self.maxsize}")
        
    
    @property
    def qsize(self) -> int:
        return self._qsize
    
    def put_nowait(self, item: T) -> bool:
        """Adds an element to the right of the queue without blocking.
        If the queue is full, raises Full."""
        
        if type(item) != self.__base_type__:
            raise TypeError("item must be of type {}".format(self.__base_type__))
        
        if self.qsize == self.maxsize:
            raise ValueError("Queue is full")
        
        self.queue.append(item)
        self._qsize += 1
        
        if self.maxsize is not None and self.qsize > self.maxsize:
            raise ValueError("Max size exceeded: {} > {}".format(self.qsize, self.maxsize))
        
        return True
    
    def get_nowait(self, block=True) -> T | None:
        """Remove and return an item from the left of the queue. Raise
        Empty if the queue is empty."""
        
        if self.qsize == 0:
            return None
        
        try:
            val = self.queue[0]
            del self.queue[0]
            self._qsize -= 1
            
            if self.maxsize is not None and self.qsize < 0:
                raise ValueError("Min size exceeded: {} < {}".format(-self.qsize, -self.maxsize))
            
            return val
        except IndexError as err:
            raise ValueError('get_nowait() called with no elements in the stack') from err
    
    def join(self) -> None:
        while