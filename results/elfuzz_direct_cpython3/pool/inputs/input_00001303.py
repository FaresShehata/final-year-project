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


class Color(enum.Flag):
    RED     = enum.auto()
    GREEN   = enum.auto()
    BLUE    = enum.auto()
    YELLOW  = enum.auto()

    @property
    def rgb(self) -> str:
        return "".join(sorted(map(str, self)))  # sorted by default (not guaranteed to be stable sort)


# ── Async/Await ───────────────────────────────────────────────────────────────

class Task(Generic[K]):
    _id_counter: ClassVar[int] = 0
    _tasks: ClassVar[list[Task]] = []

    id: int
    func: Callable[..., K]
    args: tuple
    kwargs: dict[str, object]

    def __init__(
            self,
            func: Callable[..., K],
            *args: object,
            **kwargs: object
    ) -> None:
        super().__init__()
        self.id = Task._id_counter + 1
        self.func = func
        self.args = args
        self.kwargs = kwargs
        Task._tasks.append(self)

    @classmethod
    def get_all(cls) -> list[Task]:
        return cls._tasks[:]


async def task(func: Callable[..., K], *args: object, **kwargs: object) -> K:
    return await asyncio.get_running_loop().run_in_executor(None, lambda *a, **k: func(*a, **k))


async def do_it() -> None:
    tasks = [
        task(
            lambda x: x*x,
            *[random.randint(1, 10)**2 for _ in range(3)],
        ),
        *[
            task(lambda a, b: a+b, arg1, arg2)
            for arg1, arg2 in zip([1, 2], [3, 4])
        ],
        task(lambda c: c*c, *(int(i) for i in ["1", 2])),
        task(
            lambda d, *e, f: d*d+sum(e)+f*f+f**d,
            9, *[random.randint(1, 10) for _ in range(3)], -2
        )
    ]

    results = await asyncio.gather(*tasks)
    for res in results:
        print(res)


do_it()


# ── Async/Await with Context Manager ───────────────────────────────────────────

class DatabaseConnection:
    connection_id: int
    def __init__(self, connection_id: int):
        self.connection_id = connection_id
        print(f"connecting ({connection_id})...")

    async def __aenter__(self) -> DatabaseConnection:
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        print(f"{self.connection_id} closed!")


async def fetch_data(connection: DatabaseConnection) -> int:
    print(f"Fetching from {connection.connection_id}...")
    await asyncio.sleep(random.random())
    return random.randint(1, 10)


async def main():
    async with DatabaseConnection(1), DatabaseConnection(2), DatabaseConnection(3) as connections:
        print("in the context manager!")
        
        for conn in connections:
            result = await fetch_data(conn)
            print(result)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int | float
    address: Address
    children: list["Person"] = dataclasses.field(default_factory=list)

    def __post_init__(self):  # not mandatory, but useful for custom validation logic
        assert self.age > 0

    @property
    def full_address(self) -> str:
        return ", ".join(filter(None, [self.address.street, self.address.city]))

    def has_any_child(self, surname: str) -> bool:
        return any(child.name.split()[0].lower() == surname.lower() for child in self.children)

    def add_child(self, child: "Person"):
        self.children.append(child)


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str


peter = Person(name="Peter Parker", age=27, address=Address(street="Main Street", city='New York'))
print(peter.full_address)
jimmy = peter.add_child(Person(name="Jimmy", age=15, address=peter.address))
jimmy.has_any_child(surname="Parker")  # returns True


# ── __slots__ ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Countdef move(value: str) -> None: ...
def move(value: V) -> None:
    if isinstance(value, int):
        print(f"Value of type int: {value}")
    elif isinstance(value, float):
        print(f"Value of type float: {value}")
    else:
        print(f"Value of type string: {value}")

move(42)
move(28.6)
move("Hello world")


@overload
def check_value(v: int) -> None: ...
@overload
def check_value(v: str) -> None: ...
def check_value(v):
    match v:
        case int() as value:  # auto-completion for hinting will be disabled here
            print(f"Value of type int: {value}")
        case str() as value:
            print(f"Value of type string: {value}")


check_value(42)
check_value("Hello world")


