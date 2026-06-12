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

def is_active(record: UserRecord) -> bool:
    return record["active"]

# ── NamedTuple ───────────────────────────────────────────────────────────────

UserLogEntry = namedtuple(
    "UserLogEntry",
    ["timestamp", "level", "message"],
)
TimestampedMessage = tuple[float, str]

# ── ParamSpec ────────────────────────────────────────────────────────────────

F = ParamSpec("F") # A placeholder for a function's parameters.

def map_to_string(func: F) -> Callable[F, str]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        result = func(*args, **kwargs)
        if isinstance(result, str):
            return result
        else:
            raise TypeError(f"{func.__name__} must return a string")
    return wrapper

@map_to_string
def to_camel_case(s: str) -> str:
    s = s.replace("-", " ").replace("_", " ")
    words = [word.capitalize() for word in s.split()]
    return "".join(words)

# ── ClassVar ─────────────────────────────────────────────────────────────────

class Foo(Generic[T]):
    bar: ClassVar[T]
    baz: T

    @classmethod
    def f(cls, x: T) -> None:
        cls.bar = x

foo: Foo[int] = Foo()
foo.f(123)

assert foo.bar == 123

# ── Never ───────────────────────────────────────────────────────────────────

def f(x: int, y: int) -> Never:
    return x + y // 0

try:
    print(f(1, 2))
except ZeroDivisionError:
    pass
else:
    assert False

# ── Annotated ────────────────────────────────────────────────────────────────

def log(message: str, *, level: int = 0) -> None:
    ...

log("Hello world", level=1)

Annotated[
    int,
    {
        "min_value": lambda value: value > 0,
        "max_value": lambda value: value < 10,
    }]._validate(-1)

Annotated[
    int,
    {
        "custom_check":
        lambda value: value % 2 == 0, # 2 4 6 ...
    }
]._validate(7)

Annotated[
    int,
    {
        "check_all": [
            lambda value: value > 0,
            lambda value: value < 10
        ]
    }
]._validate(-1)

Annotated[
    int,
    {
        "ignore_extra_fields": True
    }
]._validate({}) # No error because the extra fields are ignored.

Annotated[
    int,
    {
        "raise_error_on_extra_fields": True
    }
]._validate({"extra_field": 1})

Annotated[int, {"invalid_key": lambda _: ...}]._validate(123)

annotated_int: Annotated[int, {"check_all": lambda _: ...}] = 123

# ── get_type_hints ──────────────────────────────────────────────────────────

def foo(a: int, b: str, c: float) -> bool:
    return a + len(b) / c >= 0.0

return_types  = get_type_hints(foo)
print(return_types)

# ── reveal_type ─────────────────────────────────────────────────────────────

reveal_type(123)

@contextlib.contextmanager
def open_file(path: str) -> Iterator[Any]:
    yield {}

with open_file("/path/to/file.txt") as file:
    pass

def process_json(json_str: str) -> None:
    data = json.loads(json_str)
    # ...

process_json('{"key": "value"}')

@contextlib.contextmanager
def suppress_exception():
    try:
        yield
    except Exception:
        pass

with suppress_exception():
    raise ValueError("Something went wrong!")

# ── BaseException ╰─ _get_context ───────────────────────────────────────────

BaseException()._get_context()

# ── Value Error ─────────────────────────────────────────────────────────────

try:
    raise ValueError("This is an example of a raised exception.")
except ValueError as e:
    print(e)

e = 10/0
raise e from 10

# ── Annotated ───────────────────────────────────────────────────────────────

Annotated[
    10,
    {
        "description": "The number of apples on the table.",
    },
]._describe()

# ── Annotated ───────────────────────────────────────────────────────────────

from typing_extensions import Not