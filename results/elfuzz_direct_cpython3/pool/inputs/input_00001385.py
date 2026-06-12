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

class Option(TypedDict):
    value:      Optional[bool]
    description: str

Options: TypeAlias = dict[str, Option]


# ── constants ────────────────────────────────────────────────────────────────

PI: Final[float]               = 3.14159265358979323846264338327950288419716939937510582097494459230781640628620899
E: Final[float]                = 2.71828182845904523536028747135266249775724709369995
LAMBERT: Final[float]         = 0.57721566490153286060651209008240243104215933593992

# ── Classes ──────────────────────────────────────────────────────────────────

class MyClass:
    _attr: int = 42
    def method(self) -> str:
        return f"I'm {self._attr} years old."

# ── Functions ────────────────────────────────────────────────────────────────

def my_function(x: int | float) -> int:
    """This function takes a number and returns its square."""
    return x ** 2

def another_function(a: int, b: str, c: float) -> tuple[int, str]:
    """
    This function takes three arguments: an integer `a`, a string `b`,
    and a floating-point number `c`. It returns a tuple containing the sum of `a` and `c`, and the length of `b`.
    """
    result = a + c
    length = len(b)
    return result, length

# ── Generics ─────────────────────────────────────────────────────────────────

T = TypeVar("T")

class MyGenericClass(Generic[T]):
    pass


# ── Context Managers ─────────────────────────────────────────────────────────

with open("example.txt", "r") as file:
    content = file.read()

with tempfile.NamedTemporaryFile(mode="w+") as temp_file:
    temp_file.write("Hello, world!")
    temp_file.seek(0)
    data = temp_file.read()


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(my_function(5))
    print(another_function(1, "Python", 3.14))

# ────────────────────────────────────────────────────────────────────────────

"""
Defining custom type aliases with TypeAlias:

In Python, you can define your own type aliases using the TypeAlias syntax.
T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

TRandomAccessIterable       : TypeAlias = "collections.abc.Sequence[T] | collections.abc.MutableSequence[T]"
TRandomAccessIterator      : TypeAlias = "collections.abc.Iterator[T] | collections.abc.AsyncGenerator[T, S]"
TRandomAccessIterableOrStr : TypeAlias = "TRandomAccessIterable | str"
TRandomAccessIteratorOrStr: TypeAlias = "TRandomAccessIterator | str"

# ── Typing Extras ───────────────────────────────────────────────────────────-

F: Final[FloatingNumber] = 1.234
S: Final[StringLike]     = "String!"
c: Final[Complex]        = 3 + 4j
d: Final[BytesLike]      = b"Hello!"
i: Final[Integral]       = 789_123_456
o: Final[Octal]          = 0o123_456
h: Final[Hexadecimal]    = 0xABC_def
b: Final[Boolean]        = True
t: Final[Time]           = datetime.datetime(2023, 1, 1)
u: Final[NoneType]       = None
v: Final[UnionBoolIntChar] = 3 or 'A' or True
w: Final[LiteralTrueFalseNone] = False if random() < 0.5 else None

# ── numbers ABC ─────────────────────────────────────────────────────────────

if isinstance(max(integers), float):
    max_integers: Final[MaxIntegers] = max(integers)

if issubclass(min(numbers.Integral), numbers.Number):
    min_integers: Final[MinIntegers] = min(integers)

