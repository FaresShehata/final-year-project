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


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int
    status: Status = Status.PENDING


@dataclasses.dataclass(frozen=True)
class Content:
    title: str
    content: str


def serialize(c: Content) -> dict[str, object]:
    """Serialize a `Content` instance into a dictionary."""
    return dataclasses.asdict(c)


def deserialize(d: dict) -> Content:
    """Deserialize a dictionary into a `Content` instance."""
    if not isinstance(d, dict):
        raise TypeError("expected dictionary of values")
    return Content(**d)


UserDict = dict[User, Status]


@dataclasses.dataclass(frozen=True)
class AsyncFunc:
    func: Callable[..., Awaitable[V]]
    args: tuple[T, ...]
    kwargs: dict[str, T]


@dataclasses.dataclass(frozen=True)
class Result:
    value: V

    def __post_init__(self):
        assert isinstance(self.value, V), f"Expected {type(V).__name__} but got {type(self.value)}"


async def call_async_func(func: AsyncFunc) -> Result[V]:
    result: Awaitable[V] = await func.func(*func.args, **func.kwargs)
    return Result(result)


@overload
def get_status(user: User) -> Status: ...
@overload
def get_status(user_d: dict[K, V]) -> K: ...
def get_status(user_or_user_d: Union[User, dict[K, V]]) -> Union[Status, K]:
    if isinstance(user_or_user_d, User):
        user_d = user_or_user_d.__dict__
    else:
        user_d = user_or_user_d

    return user_d["status"]



# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotsUsers(dict):
    pass


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_users(users: list[User], status_filter: Status):
    for u in users:
        match u.status:
            case Status.SUCCESS:
                print(
                    f"{u.name}: "
                    f'{"you are a successful user" if status_filter == Status.SUCCESS else "not yet"}'
                )
            case Status.RUNNING:
                print(f"{u.name}: please wait...")
            case _ as