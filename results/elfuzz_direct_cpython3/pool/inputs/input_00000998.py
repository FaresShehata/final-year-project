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


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    address: Address

    class Address:
        street: str
        city: City
        zip_code: int

        def get_full_address(self) -> str:
            return f"{self.street}, {self.city.name} {self.zip_code}"

        @classmethod
        def from_street(cls, street: str) -> Address:
            return cls(street=street, city=None, zip_code=0)


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
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)


def rename_module(mod: types.ModuleType, old_name: str, new_name: str) -> None:
    """Change mod.__name__ and mod.__file__ if necessary.

    This is done by replacing the module's filename or dirname (depending on whether it's an egg).
    """
    new_filename = mod.__spec__.origin.replace(old_name, new_name).rstrip(".pyw")
    if mod.__spec__.origin.endswith(new_filename):
        mod.__name__ = new_name      # don't need to touch this
        return
    # check for eggs
    if "/.egg-info/" in mod.__spec__.origin:
        idx = mod.__spec__.origin.rfind("/.egg-info/")
        assert idx > -1, "unexpected bad egg origin"
