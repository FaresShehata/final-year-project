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


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...
    
def serialise(obj: Serialisable) -> str:
    out = json.dumps(obj.to_dict())
    print(f"serialised as string:\n{out}")
    return out


@dataclasses.dataclass(order=True, frozen=True)
class DataClass:
    int_field: int
    float_field: float
    str_field: str
    list_field: list[int]
    set_field: set[float]
    dict_field: dict[str, int]

    def to_dict(self) -> dict[K, V]:
        d = {
            "int_field": self.int_field,
            "float_field": self.float_field,
            "str_field": self.str_field,
            "list_field": self.list_field,
            "set_field": self.set_field,
            "dict_field": self.dict_field,
        }
        return d
    
    @classmethod
    def from_dict(cls, data: dict[K, V]) -> DataClass:
        d = {
            "int_field": data["int_field"],
            "float_field": data["float_field"],
            "str_field": data["str_field"],
            "list_field": data["list_field"],
            "set_field": data["set_field"],
            "dict_field": data["dict_field"],
        }
        return cls(**d)


# ── Types ────────────────────────────────────────────────────────────────────

"""
Unit types
"""
Point = tuple[float, float]
Vector = tuple[float, float]
RGB = tuple[int, int, int]


class MyInt(int): pass


class MyFloat(float): pass


MyList = list[MyInt]


"""
Generic types
"""

class GenericType(Generic[T]): ...


"""
Asyncio types
"""
async def task() -> None:
    await asyncio.sleep(random.random())


class TaskException(Exception):
    pass

async def my_task_with_exceptions():
    try:
        await asyncio.sleep(.1)
    except asyncio.CancelledError:
        raise TaskException("Task was cancelled") from BaseException
    except:
        raise TaskException("An error occurred")


# ── Walrus operator ───────────────────────────────────────────────────────────

my_list = [1, 2, 3]

item_found = False
for item in my_list:
    if item == 4:
        item_found = True
        break
else:
    item_found = False


found = any(item == 4 for item in my_list)
