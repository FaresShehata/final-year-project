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


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags[:],
            "metadata": self.metadata.copy(),
            "_history": [h.value for h in self._history],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=int(data.pop("id")),
            name=data.pop("name"),
            priority=Priority[data.pop("priority").upper()],
            status=Status[data.pop("status")]
            if data.pop("status") != "pending"
            else Status.PENDING,
            tags=[tag.lower().strip() for tag in data.pop("tags", [])],
            metadata={k: v for k, v in data.items()},
        )


def test_dataclasses() -> None:
    t1 = Task(id=123, name="hello world")
    assert t1.id == 123 and t1.name == "hello world" and t1.sort_key == -5

    t2 = Task.from_dict(t1.to_dict())
    assert t1 == t2

    t1.transition(Status.RUNNING)
    assert t1.status == Status.RUNNING

    t1.transition(Status.SUCCEEDED)
    assert t1.status == Status.SUCCEEDED and len(t1._history) == 2

    t1.transition(Status.CANCELLED)
    assert t1.status == Status.CANCELLED and len(t1._history) == 3


# ── Walrus Operator ───────────────────────────────────────────────────────────-

# https://docs.python.org/3/reference/expressions.html#evaluated-repeatedly
def add_one(x: int) -> int:
    result = x + 1
    return result


def test_walrus_operator() -> None:
    print(add_one(2))
    print((add_one(2)))
    print(((add_one(2))))
    print((((add_one(2)))))
    print(((((((add_one(2))))))))

    print(eval('x := 7'))
    print(eval('y := x * 2'))

    x = eval('x := 2')
    print(x)
    x += 3
    print(x)
    x *= 4
    print(x)
    x /= 5
    print(x)

    a, b, c = 10, 20, 30
    print(a := 20, 'b', b := 30, 'c', c

class PersonAddress(Address, serialiser): ...
Person.talk_to = "human"

class CatPerson(PersonAddress): ...


# ── Slots ─────────────────────────────────────────────────────────────────────

class Slotthorpe(dict, metaclass=dataclasses.DataClassMeta):
    """<slot>thorpe</slot>
    <ul>
    <li>Thorpe's Law: The more slots you have, the slower your program runs.</li>
    <li><a href="https://www.python.org/dev/peps/pep-3129/">PEP 3129: Implementing __slots__</a></li>
    </ul>

    >>> S = Slotthorpe([("one", 1), ("two", 2)])
    >>> print(S.one + S.two)
    3

    >>> S["three"] = 3
    Traceback (most recent call last):
    ...
    AttributeError: __slots__ does not support item assignment

    >>> del S.three
    Traceback (most recent call last):
    ...
    AttributeError: __slots__ does not support item deletion

    >>> S[4] = 4
    Traceback (most recent call last):
    ...
    KeyError: 4

    >>> del S[4]
    Traceback (most recent call last):
    ...
    KeyError: 4

    >>> S.get("four") is None
    True
    """

    __slots__: ClassVar[tuple[str, ...]] = tuple()


class Slotthorpe_1(dataclasses.dataclass):
    one: int
    two: int

    __slots__: ClassVar[tuple[str, ...]] = tuple()

    def __post_init__(self):
        super().__setattr__("three", self.one + self.two)


def test_slotthorpe() -> None:
    s = Slotthorpe([("one", 1), ("two", 2)])
    print(s.one + s.two)

    try:
        s["three"] = 3
    except AttributeError as e:
        print(e)

    try:
        del s.three
    except AttributeError as e:
        print(e)

    try:
        s[4] = 4
    except KeyError as e:
        print(e.args[0])

    try:
        del s[4]
    except KeyError as e:
        print(e.args[0])


# ── Structural Pattern Matching ────────────────────────────────────────────────

def match_person(person: Person) -> str:
    match person.addressimport xmlrpc.client
import sysconfig
import asyncio
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
