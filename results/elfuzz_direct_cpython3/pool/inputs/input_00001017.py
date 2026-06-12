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
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
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

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return len(str(value)) < 10

def non_empty_string(x: str) -> bool:
    return len(x.strip()) != 0

def check_positive_int(x: int) -> bool:
    return x >= 0

SimpleConstraint = Annotated[int, positive]
LongStr         = Annotated[str, long_str]
NonEmptyString  = Annotated[str, non_empty_string]
PositiveInt     = Annotated[int, check_positive_int]

Validated = Annotated["str", NonEmptyString, SimpleConstraint]

# ── Overload ─────────────────────────────────────────────────────────────────

class MyException(Exception): ...
class AnotherException(MyException): ...

@overload
def my_func(a: int) -> int: ...

@overload
def my_func(a: float) -> float: ...

def my_func(a: int | float) -> int | float:
    return a + 3

my_func(1)
my_func(1.0)
try:
    my_func("a")
except TypeError as e:
    print(e)
    print(e.__cause__)


# ── Context Managers ───────────────────────────────────────────────────────────

class MyContextManager(contextlib.AbstractContextManager):

    def __enter__(self) -> Anything:
        return object()

    def __exit__(
        self,
        exception_type: type[BaseException],
        exception_value: BaseException,
        traceback: TracebackType,
    ) -> None:

        raise exception_type(exception_value)



# ── Numbers ABC ───────────────────────────────────────────────────────────────

print(
    int.from_bytes(b"\x00\x13", byteorder='big'),
    int.from_bytes(b"\x00\x13", byteorder='little')
)

for n in range(-128, 129):
    print(n, hex(n))
print(binascii.hexlify(bytearray(range(128))), end="\n\n")  # noqa: E741

f = 1 / 3
print(f'{f:.1%}')
print(f'{f:,.2f}')


# ── Pathlib ───────────────────────────────────────────────────────────────────

p = pathlib.Path(__file__)
assert p.exists(), "File does not exist!"
print(p.resolve())
print(p.name)
print(p.parent)
print(p.stem)
print(p.with_stem("_new"))
print(p.absolute().resolve(strict=True))

with open(p    Literal,
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
        case Book(title="The Great Gatsby", author=author):
            print(author)
        case Book(title=title, author="J.K. Rowling"):
            print(title)
        case _ if book.rating > 4.5:
            print("Wow!")
        case _ if not isinstance(book.isbn, str):
            print("Invalid ISBN!")

# ── Walrus operator ───────────────────────────────────────────────────────────

async def do_work() -> None:
    while True:
        result = await get_data_from_db()
        if result is False:
            break
        else:
            process_result(result)


def get_data_from_db() -> bool:
    if some_condition:
        return True
    else:
        return False


# ── Generics ───────────────────────────────────────────────────────────────────

class MultiSet(Generic[T]):
    def __init__(self, *values: T) -> None:
        self._items = values[:]

    def add(self, item: T) -> None:
        self._items.append(item)

    def remove(self, item: T) -> None:
        try:
            self._items.remove(item)
        except ValueError as error:
            raise KeyError(error.args[0])

    def discard(self, item: T) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            pass

    def clear(self) -> None:
        del self._items[:]

    def union(self, other: Iterable[T]) -> MultiSet[T]:
        return MultiSet(*set(self._items).union(set(other)))

    def intersection(self, other: Iterable[T]) -> MultiSet[T]:
