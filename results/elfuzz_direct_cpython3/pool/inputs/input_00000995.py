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
    first:    str
    last:     str
    gender:   Literal["M", "F"]
    email:    str | None
    ip_address: str | None
    joined:   Seconds

def user_record_to_str(record: UserRecord) -> str:
    return f"{record['id']} {record['first']}{record['last']:>10} {record.get('gender', ''):>3}"

# ── ParamSpec ────────────────────────────────────────────────────────────────

def log_each(f: Callable[P, T]) -> Callable[..., T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        result = f(*args, **kwargs)
        print(f"{' '.join(str(arg) for arg in args)} {' '.join(f'{k}={v}' for k,v in kwargs.items())}")
        return result
    return wrapper

@log_each
def add_one(x: int, y: int) -> int:
    return x + y

print(add_one(2, 3))

# ── Annotated ────────────────────────────────────────────────────────────────

def api_call(url: str, data: Annotated[Any, "JSON"]) -> Any:
    pass

api_call("https://...", {"foo": "bar"}) # ok
# api_call("https://...", ("foo",))      # Error

# ── get_type_hints ──────────────────────────────────────────────────────────

def example_args() -> Tuple[int, str]:
    pass

def example_kwargs(a: int, b: str) -> None:
    pass

example_args()
get_type_hints(example_args)
example_kwargs(1, "string")
get_type_hints(example_kwargs)

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(get_type_hints(example_kwargs))
reveal_type(add_one.__annotations__)
reveal_type(add_one.__annotations__["return"])

# ── Never ───────────────────────────────────────────────────────────────────

def foo() -> Never:
    raise ValueError()

try:
    foo()
except ValueError:
    pass
else:
    raise Exception("Oops...")

# ── Annotated ────────────────────────────────────────────────────────────────

def get_int_from_string(string: Annotated[str, "RegexPattern(r'\d+')"]) -> int:
    match = re.search(pattern=string, string="sample")
    if not match:
        raise ValueError("Invalid input.")
    return int(match.group())

# ── ClassVar ─────────────────────────────────────────────────────────────────

class SomeClass:
    _some_var: ClassVar[str] = "this value will be shared by all instances"

s1 = SomeClass()
assert s1._some_var == "this value will be shared by all instances"
s2 = SomeClass()
assert s2._some_var == "this value will be shared by all instances"


class Foo:
    count: ClassVar[int] = 0

    @classmethod
    def increment(cls): cls.count += 1

    def __init__(self) -> None:
        self.increment()

obj1 = Foo()
assert obj1.count == 1
obj2 = Foo()
assert obj2.count == 2

#