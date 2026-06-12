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
        """Remove and return an item from the left of the queue. 
        Raise IndexError if the queue is empty.
        If optional arg block is true and the queue is empty, block until an 
        item becomes available."""
        
        if not self.queue:
            raise IndexError("Empty")
            
        item = self.queue.pop(0)
        self._qsize -= 1
        return item
    
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__}({super().__repr__()})>"
    

@runtime_checkable
class HasCancel(Protocol):
    cancel_called: bool
    
@dataclasses.dataclass(init=False)
class Task(Generic[T]):
    func: Callable[P, T]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    started: float
    done: float
    on_done: Callable[[TaskResult[T]], None] | None = dataclasses.field(default=None)
    on_cancel: Callable[[Exception], None] | None = dataclasses.field(default=None)
    
    def __init__(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
        on_done: Callable[[TaskResult[T]], None] | None = None,
        on_cancel: Callable[[Exception], None] | None = None,
    ):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.started = time.time()
        self.done = -1
        self.on_done = on_done or self.default_on_done
        self.on_cancel = on_cancel or self.default_on_cancel
        self.cancel_called = False
        
        
    def start(self) -> None:
        try:
            res = self.func(*self.args, **self.kwargs)
        except BaseException as exc:
            self.rescue(exc)
        else:
            self.result = res
            
        self.done = time.time()
        
        
    def rescue(
        self,
        exc: BaseException,
    ) -> None:
        self.cancel_called = True
        self.on_cancel(exc)
    
    
    def default_on_done(self, result):
        pass
    
    
    def default_on_cancel(self, exc):
        pass
    
    
    def cancel(self):
        if not self.cancel_called:
            self.cancel_called = True
            self.on_cancel(None)


class TaskResult(Generic[V]):
    task: Task
    result: V



class InMemoryCache(Generic[K, V]):
    _cacheimport hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    created_at: datetime.datetime

# ── NamedTuple ────────────────────────────────────────────────────────────────

class Point(NamedTuple):
    x: int
    y: int

# ── numbers ABC ──────────────────────────────────────────────────────────────

class Fraction(numbers.Rational):
    def __add__(self, other):
        # Implement addition of two Fractions here.
        pass
    
    # ... Other methods that you need to implement ...


# ── pathlib ──────────────────────────────────────────────────────────────────

file_path = pathlib.Path("/path/to/file.txt")
readme = file_path.read_text()

# ── tempfile ─────────────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as workdir:
    child = subprocess.Popen(["ls", "-l"], cwd=workdir)

# ── csv ──────────────────────────────────────────────────────────────────────

data = [["a", "b", "c"],
        ["d", "e", "f"]]
writer = csv.writer(output_file)
for row in data:
    writer.writerow(row)

reader = csv.reader(input_file)
for row in reader:
    print(row)

# ── base64 ──────────────────────────────────────────────────────────────────

encoded_data = base64.b64encode(data.encode())
decoded_data = base64.b64decode(encoded_data).decode()
