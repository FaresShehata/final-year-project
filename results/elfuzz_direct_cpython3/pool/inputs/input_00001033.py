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
import sys
import time
import traceback
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence, Set, Sized
from contextlib import suppress
from datetime import timedelta
from functools import partial
from itertools import chain, islice
from logging import DEBUG, INFO, WARNING
from numbers import Integral
from pathlib import Path
from types import GenericAlias, NoneType, TracebackType
from typing import Any, ClassVar, Literal, TypedDict, TypeGuard, TypeVar, Union, cast
from warnings import warn


class BoringException(Exception):
    pass


def dummy():
    """This function is used to make the example more readable."""
    return "dummy"


def run():
    """main entry point"""
    print("##############################")
    print("#         Seed 02            #")
    print("##############################\n")

    print("asyncio")
    a = asyncio.run(asyncio.sleep(1))
    assert a == 1.0

    await asyncio.sleep(1)
    print("Done!")

    print("\nProtocols")
    print("---------")

    class P:
        def __init__(self, x: int):
            self.x = x

        @classmethod
        def from_dict(cls, d: dict) -> P:
            return cls(d["x"])

    p = P.from_dict({"x": 1})

    class P2(P):
        def __init__(self, x: int, y: str):
            super().__init__(x)
            self.y = y

    p2 = P2.from_dict({"x": 1, "y": "abc"})
    print(p2.x)
    print(p2.y)

    class P3(P):
        pass

    p3 = P3.from_dict({"x": 1}) # type: ignore
    print(p3.x)

    with suppress(TypeError): # suppresses the error message
        P3.from_dict({}) # type: ignore

    print("\nData Classes")
    print("------------")

    @dataclasses.dataclass(eq=True, frozen=False)
    class Person:
        name: str
        age: int

    person = Person('Alice', 30)
    person2 = Person('Alice', 30)

    print(dataclasses.fields(Person))


    @dataclasses.dataclass(slots=True)
    class SlotsPerson:
        name: str
        age: int

    slots_person = SlotsPerson('Alice', 30)
    slots_person.name = 'Bob'

    print("\nStructural Pattern Matching")
    print("------------------")
    print("1")
    match { 1: "one", 2: "two" }:
        case { 1: one, 2: two } if one == "one":
            print(one, two)
        case { 1: "one" }:
            print("One only!")
        case _:
            raise ValueError("No match found.")
    print("------------------")
    print("2")
    match (1, 2):
        case (a, b):
            print(a, b)
        case (_, b):
            print(b)
    print("------------------")
    print("3")
    match (1, "hello"):
        case (1, "Hello"):
            print("Matched both cases.")
        case (a, b):
            print(a, b)
    print("------------------")
    print("4")
    match (1, "hello"):
        case (a, b) if isinstance(a, int):
            print(a, b)


    print("\ndataclasses")
    print("-------------")


    @dataclasses.dataclass
    class File:
        path: Path
        size: int

    file = File(Path.home() / "file.txt", 100_000)
    print(file.size)

    print("\nWalrus Operator")
    print("--------------")
    print(f"{(i:=1+1)}")
    while i < 10:
        print(i := i + 1)
print("Done!")


if __name__ == "__main__":
    run()


# ── Context Managers ──────────────────────────────────────────────────────────

from contextlib import contextmanager

@contextmanager
def open_file(filename: str) -> Iterator[str]:
    try:
        file = open(filename)
        yield file.read()
    finally:
        file.close()

with open_file("example.py") as content:
    print(content)

# ── Generators ───────────────────────────────────────────────────────────────

def simple_generator() -> Generator[int, None, None]:
    for i in range(5):
        yield i*i

gen = simple_generator()
for i in gen:
    print(i)

print(list(simple_generator()))

def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

seq = infinite_sequence()
next(seq) # prints 0
next(seq) # prints 1
next(seq) # prints 2


# ── Currying and Partial Application ──────────────────────────────────────────

from typing_extensions import Concatenate
from functools import wraps
from inspect import signature

def curry(func: Callable[P, T]) -> Callable[..., Callable[P, T]]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Callable[P, T]:
        sig = signature(func)
        bound_func = sig.bind_partial(*args, **kwargs).arguments
        return lambda *more_args, **moreimport ast
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

class Option(TypedDict):
    left: str
    right: str


class Line(NamedTuple):
    number: int
    line: str


class Event(NamedTuple):
    event_id: int
    timestamp: float
    message: str
    level: int


# ── Enumerations ──────────────────────────────────────────────────────────────

from enum import Enum, IntEnum, auto
import enum

SPEED: Final[int] = 90000
DIRTY: Final[bool] = True
MAGIC: Final[float] = 3.14159265358979323846264338327950288

