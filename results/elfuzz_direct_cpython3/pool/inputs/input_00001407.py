"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching, and more 🎉
"""

import datetime
import time
from typing import Awaitable, Callable, Dict, NamedTuple, Optional, Sequence, Tuple, TypeVar, Union

import enum
import functools
import inspect
import logging
import math
import random
import re
import sys
import threading
import types
import uuid
import weakref

import asyncio
import contextvars
import dataclasses
import emoji
import humanize
import ipaddress
import itertools
import jsonpickle
import multiprocessing.synchronize
import pathlib
import platformdirs
import pprint
import sqlite3
import stringcase
import statistics
import stringprep
import textwrap
import unicodedata
import weakref
import collections
import collections.abc

# ─── Generic Types ────────────────────────────────────────────────────────────
T = TypeVar("T")
KT = TypeVar("KT", bound=object)
VT = TypeVar("VT")

S = TypeVar("S")


# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-8s %(message)s",
)

logger = logging.getLogger(__name__)

# ─── Typing ───────────────────────────────────────────────────────────────────
K = TypeVar("K")
V = TypeVar("V")


<|file_sep|>/corpus/README.md
# 🐍 FastAPI 30 days

## 1. Web development fundamentals
- Build a first web app using Jinja templates, wsgi, middleware, route handlers, static files, form features, and cookies
- Use Python's asyncio library to build asynchronous web apps that scale
- Understand what it means to develop a server-side application using Flask, FastAPI, Starlette, uvicorn, aiohttp, hypercorn, and others

## 2. Web frameworks
- Learn what is meant by a web framework, understand how your code interacts with the framework, and write a simple REST API using FastAPI
- Write an API endpoint that returns information about the calling environment, including the request method, header fields, query parameters, body content, remote address, and system time
- Create an HTTP client that requests a JSON representation of a route from an instance of FastAPI and parses it into a Python object
- Use the FastAPI Router class to group routes together
- Create a simple web app using FastAPI that receives two numbers# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────
@runtime_checkable
class AsyncIterable(Protocol[K], Iterable[K]):
    async def __aiter__(self) -> AsyncIterator[K]: ...


async def _next(iterable: AsyncIterable[K]) -> K:
    async for x in iterable:
        return x


async def next_or_none(iterable: AsyncIterable[K]) -> K | None:
    try:
        return await _next(iterable)
    except StopAsyncIteration:
        return None


async def first(iterable: AsyncIterable[K]) -> K:
    return await _next(iterable)


async def last(iterable: AsyncIterable[K]) -> K:
    rev_iter = reversed(list(iterable))
    return await _next(rev_iter)


async def all_async(iterable: AsyncIterable[V]) -> bool:
    done = False
    for item in iterable:
        if done:
            break
        done = True
    return done


async def some_async(iterable: AsyncIterable[V]) -> bool:
    found = False
    async for item in iterable:
        if not found:
            found = True
    return found


async def count_async(iterable: AsyncIterable[V]) -> int:
    cnt = 0
    async for x in iterable:
        cnt += 1
    return cnt


async def find_first_async(iterable: AsyncIterable[V]) -> V | None:
    first_found = False
    for item in iterable:
        if first_found or not isinstance(item, S):
            continue
        first_found = True
        return item
    return None


async def find_last_async(iterable: AsyncIterable[V]) -> V | None:
    first_found = False
    for item in reversed(list(iterable)):
        if first_found or not isinstance(item, S):
            continue
        first_found = True
        return item
    return None


async def partition_async(iterable: AsyncIterable[V]) -> tuple[list[V], list[V]]:
    left = []
    right = []

    for x in iterable:
        if len(left) < len(right):
            left.append(x)
        else:
            right.append(x)

    return (left, right)



class FunctionWrapper:
    def __init__(self, func: Callable[..., None]) -> None:
        self.func = func

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        print(f"Calling function: {func.__module__}.{func.__name__}")
        self.func(*args, **kwargs)


def wrapper(func: Callable[..., None]) -> None:
    print(f"Calling wrapper(): {func.__module__}.{func.__name__}")

    def wrapped_func(*args: Any, **kwargs: Any) -> None:
        print(f"Calling wrapper().wrapped_func()")
        func(*args, **kwargs)

    return wrapped_func


# ── Context managers ───────────────────────────────────────────────────────────

class CounterContextManager:
    def __enter__(self) -> None:
        self.counter = 0

    defJsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    constraint: tuple[Any, ...]
    args:       tuple[int, int]

    def __init__(self, annotation: type[_Constrained], *args: Any, **kwargs: Any) -> None:
        self.constraint = kwargs.pop("_constraint", ())
        self.args = args
        super().__init__(annotation, *args, **kwargs)

    @property
    def _name(self) -> str:
        return str(type(self)).split("'")[1].split(".")[-1]

    def __get__(self, obj: Any, cls: type[Any]) -> Any:
        result = getattr(obj, "_" + self._name, None)
        if result is None:
            raise AttributeError(
                f"No such attribute '{self._name}' "
                f"in instance of type {type(cls).__qualname__}",
            )
        return result

    def __set__(self, obj: Any, value: Any) -> None:
        expected_types = [t.__origin__ for t in self.constraint]
        fail_msg = (
            f"'{value}' ({type(value)}) does not match one of the following types: "
            + ", ".join([t.__name__ for t in expected_types])
        )

        if any(isinstance(value, tp) for tp in expected_types):
            setattr(obj, "_" + self._name, value)
            return

        raise TypeError(fail_msg)

    def __repr__(self) -> str:
        return repr(getattr(self, "_name")) + "." + super().__repr__()



@Annotated[
    _Constrained[int, int],
    "This value must be an integer between 1 and 10",
]
def constrained_function(x: int) -> None:
    pass



# ── ParamSpec ─────────────────────────────────────────────────────────────────

ParamSpec1: TypeAlias = ParamSpec["ParamSpec1"]
ParamSpec2: TypeAlias = ParamSpec["ParamSpec2"]


def foo(*a: ParamSpec1, **kw: ParamSpec2) -> None:
    ...


foo(1, x="abc", y=2.5)
foo(1, 2, 3, {"x": "y"})  # Error!


# ── Concatenate ───────────────────────────────────────────────────────────────

Concatenate[T, Tuple[X]]: TypeAlias = T | Tuple[X]


Concatenate[str, Tuple[int]]: str
Concatenate["hello world", Tupleimport types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
