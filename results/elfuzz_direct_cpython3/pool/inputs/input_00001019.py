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
    x: int
    y: int

@dataclasses.dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

@dataclasses.dataclass(init=False, order=True)
class Student:
    name: str
    grade: int

    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade


# ── Slots ─────────────────────────────────────────────────────────────────────

class Person(dataclasses.DataClass):
    __slots__: ClassVar[list[str]] = ["name", "_age"]
    age: int

p = Person(name="John", age=36)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match(subject: T, cases: dict[Tuple[object], V]) -> V:
    """Pattern matching for Python.

    Args:
      subject (Any): The value to be matched.
      cases (dict[tuple of object, V]): A dictionary mapping patterns to values.

    Returns:
       V: The corresponding value if a match is found.
    """
    for pattern, value in cases.items():
        if all(isinstance(x, type(y)) and x == y for x, y in zip(pattern, subject)):
            return value
    raise ValueError("No case matches")


@match
def example_match(something: int | str | list[int]):
    match something:
        case 42:
            print("The answer")
        case "hello":
            print("Greetings Earthling!")
        case [a]:
            print(a)
        case []:
            print("Nothing here.")
        case _:
            print("Unknown input.")

example_match([1, 2, 3])

# ── Walrus Operator ───────────────────────────────────────────────────────────

r"""Unpacking of a tuple into variables with the walrus operator """
x, y = (1, 2)
print(x, y)

r"""Unpacking of a literal sequence into multiple variables with the walrus operator """
(**{y: x})
print(x, y)

r"""Unpacking of a string into variables with the walrus operator """
(*names), last_name = ("Alice", "Bob", "Charlie")
print(names, last_name)

r"""Unpacking of a generator expression into variables with the walrus operator """
(*names), last_name = (n.lower() for n in {"Alice", "Bob"})
print(names, last_name
import ast
import collections.abc as c_abc
import csv
import dataclasses
import functools
import glob
import hashlib
import html
import itertools
import json
import logging
import math
import operator
import pickle
import pprint
import re
import shutil
import signal
import sys
import tempfile
import timeit
import types
import tokenize
import warnings
from collections import Counter, defaultdict, deque
from contextlib import (
    suppress,
    redirect_stdout as _redirect_stdout,
    AbstractContextManager as _AbstractContextManager,
)
from enum import Enum
from functools import partial, wraps
from io import TextIOWrapper
from itertools import chain, dropwhile, islice, tee, zip_longest
from multiprocessing import Queue, Value
from multiprocessing.connection import Listener
from multiprocessing.reduction import ReductionError
from numbers import Real
from pathlib import PureWindowsPath
from queue import Empty
from random import sample
from re import Pattern as r_Pattern
from re import search as r_search, sub as r_sub
from statistics import mean
from textwrap import dedent, wrap as twrap
from token import Name, Number, String
from tokenize import generate_tokens
from typing import (
    Any,
    Callable,
    Collection,
    ContextManager,
    Iterable,
    Iterator,
    List,
    Mapping,
    Tuple,
    Union,
)
from unittest.mock import patch as u_patch

from hypothesis.strategies import composite as h_composite
from hypothesis.strategies import integers as h_integers
from hypothesis.strategies import lists as h_lists
from hypothesis.strategies import one_of as h_one_of
from hypothesis.strategies import sets as h_sets
from hypothesis.strategies import tuples as h_tuples
from hypothesis.strategies import text as h_text
from hypothesis.strategies import booleans as h_booleans
from hypothesis.strategies import fixed_dictionaries as h_fixed_dictionaries
from hypothesis.strategies import dictionaries as h_dictionaries
from hypothesis.strategies import floats as h_floats
from hypothesis.strategies import symbolic as h_symbolic
from hypothesis.strategies import recursive as h_recursive
from hypothesis.strategies import none as h_none
from hypothesis.strategies import complex_numbers as h_complex_numbers
from hypothesis.strategies import datetimes as h_datetimes
from hypothesis.strategies import dates as h_dates
from hypothesis.strategies import times as h_times
from hypothesis.strategies import datetimes as h_datetimes
from hypothesis.strategies import uuids as h_uuids
from hypothesis.strategies import from_type as h_from_type
from hypothesis.strategies import from_regex as h_from_regex
from hypothesis.strategies import just as h_just
from hypothesis.strategies import strings as h_strings
from hypothesis.strategies import binary as h_binary
from hypothesis.strategies import booleans as h_booleans
from hypothesis.strategies import composite as h_composite
from hypothesis.strategies import data as h_data
from hypothesis.strategies import dictionaries as h_dictionaries
from hypothesis.strategies import frozensets as h_frozensets
from hypothesis.strategies import integers as h_integers
from hypothesis.strategies import lists as h_lists
from hypothesis.strategies import nested as h_nested
from hypothesis.strategies import sampled_from as h_sampled_from
from hypothesis.strategies import sets as h_sets
