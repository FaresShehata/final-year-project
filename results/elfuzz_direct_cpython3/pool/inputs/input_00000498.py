"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Set
from dataclasses import dataclass, field
from functools import partial
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from itertools import chain, cycle, dropwhile, groupby, tee
from types import GeneratorType, UnionType
from types import ModuleType as _ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    overload,
    runtime_checkable,
)


T = TypeVar("T")
U = TypeVar("U")


# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(str, enum.Enum):
    PENDING         = "pending"
    RUNNING         = "running"
    COMPLETED       = "completed"
    FAILED          = "failed"

    def __str__(self) -> str:
        return self.value.upper()


@dataclass(frozen=True, slots=True)
class TransactionStatuses:
    pending: bool
    running: bool
    completed: bool
    failed: bool

    def __init__(
        self,
        pending: bool = False,
        running: bool = True,
        completed: bool = True,
        failed: bool = False,
    ):
        object.__setattr__(self, "_asdict_", {"pending": pending, "running": running, "completed": completed, "failed": failed})


# ── Generators ────────────────────────────────────────────────────────────────


def yelder(gen_func: Callable[..., T]) -> Callable[..., Generator[T, None, None]]:
    @overload
    def wrapper(*args: Any, **kwargs: Any) -> Generator[T, None, None]: ...
    
    @overload
    def wrapper(*args: Any, **kwargs: Any) -> T: ...

    def wrapper(*args: Any, **kwargs: Any) -> Generator[T, None, None]:
        gen = gen_func(*args, **kwargs)
        try:
            yield from gen
        finally:
            gen.close()

    return wrapper


def iter_cycler(iterable: Iterable[T], steps=1) -> Iterator[Tuple[int, T]]: 
    i = 0  
    iters = tee(cycle(iterable), steps)
    next(iters[i], ...)  
    return zip(chain.from_iterable(iters), range(steps))


def timer(func_or_gen: Callable[..., T] | GeneratorType) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        result = func_or_gen(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Timer: {duration} seconds")
        return result

    return wrapper


# ── Data classes ──────────────────────────────────────────────────────────────

from datetime import datetime
from decimal import Decimal
from random import randint
from uuid import UUID

@dataclass(slots=True)
class Person:
    first_name: str
    last_name: str
    age: int
    birthday: datetime.date
    email: Optional[str] = None
    phone_number: Optional[str] = None
    social_id: Optional[UUID] = None
    balance: Optional[Decimal] = None
    friends    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def get_function_call_stack() -> list[types.FrameType]:
    """Get all frames on our call stack by walking the traceback."""
    tb = sys.exc_info()[2]
    frames: list[types.FrameType] = []
    while tb is not None:
        frame = tb.tb_frame
        if frame is not None:
            frames.append(frame)
        tb = tb.tb_next
    return frames


def print_stack_depth(stack: list[types.FrameType]) -> None:
    """Print out a table showing each frame's depth, name, and locals."""
    widths = [max(len(name) or "", len(str(loc))) for loc in zip(*stack)]
    format_str = ("|%%-%ds | %%-30s | " + "%-" + str(width - 6) + "s") * len(stack[-1].f_locals)
    max_len = sum(widths) + len(format_str) - 1
    sep = "+%s+" % "+" + "-".join(["-" * w for w in widths])
    print(sep)
    print("|   %-7s |     %-30s | %-" + str(max_len - 9) + "s")
    print(sep)
    print(format_str % tuple(("Depth", "Name", "Locals")))
    print(sep)
    for frame in reversed(stack):
        print(" ".join([f"{n:<{w}}" for n, w in zip((len(stack) - idx, frame.f_code.co_name, repr(frame.f_locals)), widths)]))


# ── GC tracing ────────────────────────────────────────────────────────────────

def trace_reachable(obj: Any) -> set[Any]:
    reachable: set[Any] = set()
    seen: set[Any] = set()

    def explore(o: Any) -> None:
        if isinstance(o, (list, tuple)):
            for e in o:
                explore(e)
        elif isinstance(o, dict):
            for k in o.keys():
                explore(k)
            for v in o.values():
                explore(v)
        elif id(o) not in seen:
            seen.add(id(o))
            reachable.add(o)

