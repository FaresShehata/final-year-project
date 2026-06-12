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
    defaults={ "level": "INFO" },
)

user_log_entry: UserLogEntry = UserLogEntry(timestamp=time.time(), **{"message": "Hello world"})
assert user_log_entry.level == "INFO"

# ── ParamSpec ────────────────────────────────────────────────────────────────

def add(a: int, b: int, /, c: int = 0) -> int:
    ...

add.__signature__

ParamSpecsFoo = ParamSpec("foo")
ParamSpecsBar = ParamSpec("bar")

def foo(x: int, f: Callable[..., int]) -> None:
    ...

foo.__annotations__["f"] == Callable[ParamSpecsFoo, int]
foo.__annotations__["x"].name == "x"
foo.__annotations__["x"].kind == Parameter.POSITIONAL_OR_KEYWORD

def bar(f: Callable[ParamSpecsFoo, int], x: int, y: int, z: int) -> None:
    ...

bar.__annotations__["f"].parameters["x"].name == "y"
bar.__annotations__["f"].parameters["z"].default == 0

# ── Concatenate ──────────────────────────────────────────────────────────────

ConcatenatesNamedTuple = NamedTuple(
    "ConcatenatesNamedTuple",
    [("a", int), ("b", float)],
)
OtherNamedTuple = NamedTuple("OtherNamedTuple", [("c", str)])
ConcatenatesOtherNamedTuple = concatnate(ConcatenatesNamedTuple, OtherNamedTuple)

# ── Never ───────────────────────────────────────────────────────────────────

NeverSomething = Never[T]
never_something: NeverSomething = 123

# ── Annotated ────────────────────────────────────────────────────────────────

AnnotatedInt = Annotated[int, {"min_value": lambda _: _ >= 0}]
AnnotatedFloat = Annotated[float, {"max_value": lambda _: _ <= 1.0}]
AnnotatedStr = Annotated[str, {"min_length": 3, "max_length": 8}]

AnnotatedInt._validate(123)
AnnotatedInt._validate(-1)

AnnotatedInt._validate(1.2) # Error
AnnotatedInt._validate(None) # Error

AnnotatedInt._get_validator(min_value=1)(-1) # Error
AnnotatedInt._get_validator(max_value=1)(123) # Error

# ── get_type_h    assert False

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

