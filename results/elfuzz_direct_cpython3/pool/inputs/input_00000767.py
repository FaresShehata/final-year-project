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
    COMPLETED = "completed"


@runtime_checkable
class Node(Protocol[K]):
    def link(self, other: Node[K]) -> None:
        ...

    @property
    def value(self) -> K: ...
    
    def __str__(self) -> str:
        ...


@runtime_checkable
class TimeSynchronizedNode(Node[str], Protocol):
    @property
    def timestamp(self) -> float: ...


# ─── Structures ──────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Task(Generic[T]):
    """A task that can be executed."""

    func: Callable[[], Awaitable[T]]
    result: T | None = None
    
    def await_result(
            self,
            *,
            timeout: float | None = None,
            delay: float = 1.0,
    ) -> T:
        if self.result is not None:
            return self.result
        
        loop = asyncio.get_running_loop()
        
        while True:
            try:
                return loop.run_until_complete(self.func())
            
            except asyncio.TimeoutError as exc:
                self.result = exc
            
            finally:
                if timeout is None or timeout < 0:
                    break
                
                now = time.monotonic() + delay
                deadline = min(now + timeout, now)
                await asyncio.sleep(deadline - now)


@dataclasses.dataclass(frozen=True)
class Operation:
    name: str
    args: tuple[object]
    kwargs: dict[str, object]


def apply_operation(operation: Operation, *args: object, **kwargs: object) -> object:
    """Apply an operation to some arguments and keyword arguments."""
    func_name = f"{operation.name}_"
    
    for arg in args:
        func_name += type(arg).__name__
    
    for key, val in kwargs.items():
        func_name += f"{key}_{type(val).__name__}"
    
    func_name += "_"

    eval_statement = f'lambda {",".join([arg.__name__ for arg in args])}: ' \
                     f'{func_name}{type(kwargs)}({", ".join(map(str, kwargs.values()))})'
                    
    return eval(eval_statement)(*args)



# ─── Utilities ───────────────────────────────────────────────────────────────


def compare_lists(left: list[V], right: list[V]) -> int:
    """Compare two lists of values recursively."""
    left