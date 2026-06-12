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
    def wrapper(*args: Any, **kwargs: Any) -> Awaitable[Generator[T, None, None]]: ...
    
    def wrapper(*args: Any, **kwargs: Any) -> Generator[T, None, None] | Awaitable[Generator[T, None, None]]:
        if isinstance(gen_func(*args, **kwargs), GeneratorType):
            gen_obj = gen_func(*args, **kwargs)
            assert isinstance(gen_obj, GeneratorType)
            return gen_obj
    
        else:
            gen_coro = gen_func(*args, **kwargs)
            assert not isinstance(gen_coro, GeneratorType) and iscoroutinefunction(gen_coro)
            
            async def gen_wrapper() -> Generator[T, None, None]:
                yield from gen_coro
                
            return gen_wrapper()
        
    return wrapper


# ── Async Funcs ──────────────────────────────────────────────────────────────


@yelder
async def awaiter(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Wrap a function in an asynchronous context.
    """
    return func(*args, **kwargs)

@yelder
async def run_all_async_funcs(
    funcs: Iterable[Callable[..., Coroutine]], 
    no_blocking: bool = False, 
    blocking_timeout: Optional[float] = None,
    max_concurrent_tasks: int = 1
) -> None:
    """Run all given async functions concurrently."""
    tasks = [loop.create_task(awaiter(func)) for func in funcs]
    await wait_any(tasks, no_blocking=no_blocking, blocking_timeout=blocking_timeout, max_concurrent=max_concurrent_tasks) 

async def wait_any(
    tasks: Iterable[Awaitable],
    no_blocking: bool = False,
    blocking_timeout: Optional[float] = None,
    max_concurrent: int = 1
) -> None:
    """
    Wait until any of the given tasks finishes.

    Args:
        tasks (Iterable[Task]): The tasks to wait on.
        no_blocking (bool, optional): If true, don't block until any task finishes.
            Defaults to False.
        blocking_timeout (Optional[float], optional): The maximum time to wait.
            Defaults to None.
        max_concurrent (int, optional): The maximum number of concurrent tasks to allow.
            Defaults to 1.
    """

    # Get the task objects and their statuses.
    tasks_and_statuses = get_tasks_and