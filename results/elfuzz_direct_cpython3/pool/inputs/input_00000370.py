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

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5



# ── Slots ─────────────────────────────────────────────────────────────────────

class MyDataClassWithSlots():
    __slots__ = ("foo", "bar")

    def __init__(self, foo: int, bar: str) -> None:
        self.foo = foo
        self.bar = bar


# ── Structural Patterns Matching ───────────────────────────────────────────────

class User:
    def __init__(self, id_: int, username: str) -> None:
        self.id_ = id_
        self.username = username

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id_})"


class Role(User):
    def __init__(self, id_: int, username: str, permissions: set[str]) -> None:
        super().__init__(id_, username)
        self.permissions = permissions


def get_user(user_id: int, users: list[User]) -> User | None:
    user = next((u for u in users if u.id_ == user_id), None)
    if not user:
        return None
    elif isinstance(user, Role):
        return user
    return user


users: list[User] = []

user = get_user(1, users)
if isinstance(user, User):
    print(user)
elif isinstance(user, Role):
    print(user, user.permissions)



# ── Walrus Operator ───────────────────────────────────────────────────────────

# Using assignment expressions with generators.

async def process_data(generator: Generator[T, T, None], *args: T, **kwargs: T) -> T:
    result = await generator.send(None)
    for arg in args:
        result = await generator.send(arg)
    for key, value in kwargs.items():
        result = await generator.send((key, value))
    return result


# ── Typing Generics ───────────────────────────────────────────────────────────-

# The following code is equivalent to:

#     class MyDict(dict):
#         pass


MyDict = dict[str, Any]


# ── Asyncio ───────────────────────────────────────────────────────────────────

async def main() -> None:
    async def worker(task_id: int) -> int:
        await asyncio.sleep(random.random())
        return task_id

    tasks = []
    for i in range(5):
        task = asyncio.create_task(worker(i))
        tasks.append(task)

    done, pending = await asyncio.wait(tasks, timeout=2.0, return_when=asyncio.ALL_COMPLETED)
    for task in done:
        print(await task)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())


# ── Generators ─────────────────────────    # ── Generics and type hints ─────────────────────────────────────────────────

    class Vector(Generic[K]):
        def __init__(self, origin_x: K, origin_y: K, destination_x: K, destination_y: K) -> None:
            self.origin = Point(origin_x, origin_y)
            self.destination = Point(destination_x, destination_y)


    # ── Structural Pattern Matching ─────────────────────────────────────────────

    def parse_json(json_str: str) -> dict[str, Any]:
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(e.msg) from e
        else:
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected a dictionary but got {type(parsed)} instead.")
            return parsed


    data = """
        {
            "name": "John Doe",
            "age": 43,
            "phones": [
                "+44 1234567",
                "+44 2345678"
            ]
        }
    """

    try:
        data = parse_json(data)
        name = data["name"]
        age = data["age"]
        phones = [phone for phone in data["phones"]]
    except ValueError as e:
        print(e)


    # ── Walrus Operator ─────────────────────────────────────────────────────────

    # The walrus operator helps you avoid writing unnecessary parentheses.
    # For example, this expression:
    #
    #     `a := b.get('x', default)`
    #
    # Is equivalent to the following without it:
    #
    #     `a = b.get('x', default)`

    # ── Typing Generics ─