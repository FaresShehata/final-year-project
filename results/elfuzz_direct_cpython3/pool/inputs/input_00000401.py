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
        lambda value: value % 2 == 0,
        "another_custom_check":
        lambda value: value % 7 != 0,
    }
]._validate(18)

Annotated[
    int,
    {
        "custom_check":
        lambda value: value % 2 == 0,
        "another_custom_check":
        lambda value: value % 7 == 0,
    }
]._validate(19)

A: Annotated[int, {"custom_check": lambda _: True}] = 4
reveal_type(A)

B: Annotated[int, {"custom_check": lambda _: False}] = 4
reveal_type(B)

C: Annotated[int, {"invalid_key": lambda _: True}] = 4

D: Annotated[int, {"custom_check": lambda _: True, "an_invalid_key": lambda _: True}] = 4
reveal_type(D)

E: Annotated[int, {}] = 4

reveal_type(E)


# ── Annotated ────────────────────────────────────────────────────────────────

# class MyTypeGuard:
#     def __call__(self, x: object) -> bool:
#         return type(x) == int and x >= 0
#
# my_typeguard = MyTypeGuard()
# reveal_type(my_typeguard)

MyEnum = Enum("MyEnum", [("FOO", 1), ("BAR", 2)])

def test_my_enum(value: int) -> MyEnum:
    ... # TODO


# ── Annotated ────────────────────────────────────────────────────────────────

# class Message(NamedTuple): # TODO
#     content: str
#
# message: Message = Message(content="Hello, world!")
# reveal_type(message.content)


# ── Annotated ────────────────────────────────────────────────────────────────

# class MyClass:
#     @property
#     def my_property(self) -> Annotated[int, {"min_value": lambda v: v > 0}]:

#         return self._my_property
#     @my_property.setter
#     def my_property(self, value: Annotated[int, {"min_value": lambda v: v > 0}]) -> None:

#         self._my_property = value

# class ClassWithPrivateProperty:
#     _private_property: Annotated[int, {"min_value": lambda v: v >