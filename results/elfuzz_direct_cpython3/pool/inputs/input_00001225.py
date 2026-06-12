"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NoReturn,
    Optional,
    Tuple,
    Union,
    overload,
    TYPE_CHECKING,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    get_type_hints_from_call,
    Literal,
    TypeVar,
    TypeGuard,
    Protocol,
    runtime_checkable,
    TypeAlias,
)
import sys
import types
import weakref

if TYPE_CHECKING:
    from collections.abc import Sequence
    S = TypeVar("S", bound=Sequence[Any])
else:
    S = TypeVar("S", bound="Sequence[Any]")


# ── Assertions ───────────────────────────────────────────────────────────────

assert isinstance(b"a", bytes)
assert isinstance(a := b"a".decode(), str)
assert any([a])

for i in range(3): assert a + b"\x00\x01"

try:
    assert a + "\x00\x01"
except TypeError:
    pass

try:
    assert a + ("\x00\x01",)
except TypeError:
    pass

try:
    assert a + [b"\x00\x01"]
except TypeError:
    pass

try:
    assert a + [[b"\x00\x01"]]
except TypeError:
    pass

try:
    assert a + {"one": b"\x00\x01"}
except TypeError:
    pass

try:
    assert a + {"one": b"\x00\x01"}["one"]
except TypeError:
    pass

try:
    assert a + ["\x00\x01"]
except TypeError:
    pass

try:
    assert a + [(b"\x00\x01")]
except TypeError:
    pass

try:
    assert a + [{b"\x00\x01": b"\x00\x01"}]
except TypeError:
    pass

try:
    assert a + [{"a": "\x00\x01"}, ]
except TypeError:
    pass

try:
    assert a + [{"a": []}, ]
except TypeError:
    pass

try:
    assert a + [{"a": ()}]
except TypeError:
    pass

try:
    assert a + [{"a": {}}, ]
except TypeError:
    pass

try:
    assert a + [{"a": set()}, ]
except TypeError:
    pass

try:
    assert a + [{"a": frozenset()}]
except TypeError:
    pass

try:
    assert a + [{"a": bytearray()}]
except TypeError:
    pass

try:
    assert a + [{"a": b"1"}, ]
except TypeError:
    pass

try:
    assert a + [{"a": c""}, ]
except TypeError:
    pass

try:
    assert a + [{"a": ""}, ]
except TypeError:
    pass

try:
    assert a + [{"a": f""}, ]
except TypeError:
    pass

try:
    assert a + [{"a": r""}, ]
except TypeError:
    pass

try:
    assert a + [{"a": ''}, ]
except TypeError:
    pass

try:
    assert a + [{"a": u''}, ]
except TypeError:
    pass

try:
    assert a + [{"a": lambda x: x}]
except TypeError:
    pass

try:
    assert a + [{"a": 0}, ]
except TypeError:
    pass

try:
    assert a + [{"a": True}, ]
except TypeError:
    pass

try:
    assert a + [{"a": False}, ]
except TypeError:
    pass

try:
    assert a + [{"a": object()}, ]
except TypeError:
    pass

try:
    assert a + [{"a": iter([])}, ]
except TypeError:
    pass

try:
    assert a + [{"a": enumerate([])}, ]
except TypeError:
    pass

try:
    assert a + [{"a": reversed([])}, ]
except TypeError:
    pass

try:
    assert a + [{"a": tuple([])}, ]
except TypeError:
    pass

try:
    assert a + [{"a": list([])}, ]
except TypeError:
    pass

try
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


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Address:
    street_number: str
    street_name: str
    city: str


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    last_name: str
    age: int
    address: Address
    friends: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    isbn: int
    rating: float = 0.0


# ── Slots ─────────────────────────────────────────────────────────────────────

Person.__slots__ = ("name", "last_name")
Book.__slots__ = ("title", "author")


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person) -> None:
    match person:
        case Person(name="John Smith"):
            print("Hello John!")
        case Person(last_name="Doe"):
            print("Hi there!")
        case _:
            print("Welcome!")


def match_book(book: Book) -> None:
    match book:
        case Book(title="The Hitchhiker's Guide to the Galaxy",
                  author="Douglas Adams", isbn=978-0345396424):
            print("This is a classic!")
        case Book(_, _, isbn=isbn, rating > 4.5):
            print("This is a fantastic book!")
        case _:
            print("We don't know about this book.")


# ── Walrus Operator ───────────────────────────────────────────────────────────

def count_words(text: str) -> Counter[str]:
    result: Counter[str] = Counter()
    while word := text.pop():
        result[word] += 1
    return result


# ── Generics ───────────────────────────────────────────────────────────────────

class Queue(Generic[K]):
    def __init__(self) -> None:
        self._elements: list[tuple[float, K]] = []

    def enqueue(self, key: K, priority: float = 0.0) -> None:
        index = bisect.bisect_left([e[0] for e in self._elements], priority)
        self._elements.insert(index, (priority, key))

    def dequeue(self) -> K:
        return self._elements.pop()[1]

    def pop_all(self) -> list[K]:
        elements = self._elements.copy()
        self.clear()
        return [element[1] for element in elements]

    def clear(self) -> None:
        self._elements.clear()


class PriorityQueue(Generic[T]):
    def __init__(self) -> None:
        self._queue: list[tuple[float, T]] = []
        self._index: int = 0

    def insert(self, item: T, priority: float = 0.0) -> None:
