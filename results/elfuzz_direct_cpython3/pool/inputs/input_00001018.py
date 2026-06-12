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
# This will allow your code to check whether instances of your classes conform
# to this protocol at runtime, without requiring them to be checked at compile
# time.

# ─────────────────────────────────────────────────────────────────────────────
#
# You can also define an abstract base class (ABC) that acts as a protocol using
# the abc module:

from abc import ABCMeta, abstractmethod

class IMyProtocol(metaclass=ABCMeta):
    @abstractmethod
    def my_method(self) -> None:
        ...

# ─────────────────────────────────────────────────────────────────────────────
#
# The third option is to use the 'typing_extensions' module's '_ProtocolMetaclass'.
# This meta-class provides similar functionality to the 'runtime_checkable'
# decorator but allows for the creation of generic protocols, which were not
# possible with the original _Protocol metaclass.

from typing_extensions import _ProtocolMetaclass

class IMyGenericProtocol(_ProtocolMetaclass[T]):
    @abstractmethod
    def my_method(self, x: T) -> None:
        ...

# ─────────────────────────────────────────────────────────────────────────────
#
# Note that these approaches provide different levels of support for type hints
# and static type checking:
#
# * Using the 'runtime_checkable' decorator or the 'abc' module ensures that
#   type-checking errors are raised during development.
# * Defining an ABC or using the '_ProtocolMetaclass' for generic protocols may
#   improve performance by allowing the implementation of concrete methods, but
#   it comes with limitations regarding the use of generic types within those
#   protocols.
#

# ── Structural Pattern Matching ----------------------------------------------

# ─────────────────────────────────────────────────────────────────────────────
#
# Structural pattern matching was introduced in Python 3.10 and allows for more
# concise and readable control flow based on the structure of values instead of
# their identity.

match_item = {
    "id": 1234,
    "text": "Hello World",
    "price": 9.99,
}

match match_item:
    case {"name": name, "age": age}:
        print(f"{name} is {age}")
    case {"name": name, **other}:
        print(f"Name: {name}, Other keys: {list(other.keys())}")

# ─────────────────────────────────────────────────────────────────────────