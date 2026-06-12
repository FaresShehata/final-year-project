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

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20

# ── Data Classes --------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Item:
    id : int
    text : str
    price : float
    available : bool = True
    category : str | None = None


# ── Generics and Type Variables -----------------------------------------------


async def do_something_async() -> int:
    await asyncio.sleep(random.uniform(0.0, 2))
    return random.randint(1, 3)


def some_function(k: K, v: V) -> tuple[K, V]:
    ...


async def test_generics() -> None:
    loop = asyncio.get_running_loop()
    t_start = loop.time()
    result = await loop.run_in_executor(None, do_something_async())
    print(result)
    t_end = loop.time()
    delta_t = t_end - t_start
    print(delta_t)


# ── Protocols -----------------------------------------------------------------

# ─────────────────────────────────────────────────────────────────────────────
#
# In Python 3.8+, you can use the `runtime_checkable` decorator from 'typing'
# to specify that a protocol is intended for run-time type checking only.
#
# For example, you could define a protocol like this:
# --------------------------------------------------------
# @runtime_checkable
# class MyProtocol(Protocol):
#     def my_method(self) -> None:
#         ...
# --------------------------------------------------------
#
# The 'runtime_checkable' decorator makes it possible to use the protocol as a
# type hint or a runtime-checking mechanism without enforcing static type checking.


@runtime_checkable
class AsyncIterable(Protocol[T]):
    def __aiter__(self) -> AsyncIterator[T]: ...
    async def __anext__(self): ...



# ── Slots -------------------------------------------------------------------------


class Person:

    __slots__ = ("id", "first_name", "last_name")


person = Person(id=42, first_name="John", last_name="Doe")


# ── Structural Pattern Matching -----------------------------------------------


class Movie:
    title: str
    year: int
    rating: float
    genres: list[str]


movie = {
    "title": "The Matrix",
    "year": 1999,
    "rating": 8.7,
    "genres": ["Science Fiction", "Action"],
}

match movie:
    case {"title": title, "year": year, "rating": rating, "genres": genre_list}: 
        print(title,    def property_b(self, value: str) -> None:
        pass

    @staticmethod
    def static_method_b(arg: str) -> str:
        return "b-" + arg

    @classmethod
    def class_method_b(cls, arg: str) -> str:
        return "b-" + arg


# ── Decorators ───────────────────────────────────────────────────────────────-

def check_type(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        for name, value in bound_args.arguments.items():
            expected_types = getattr(
                func, "_expected_types_", {}
            ).get(name)
            if expected_types is not None:
                assert isinstance(value, expected_types), f"Expected {value} to be an instance of {expected        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


