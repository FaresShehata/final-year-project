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
        lambda value: value % 2 == 0, # noqa
        "other_custom_check":
        lambda value: value > 0 and value < 10, # noqa
    }
]._validate(9)

TypeError: The given annotation does not allow this usage

# ── get_type_hints ──────────────────────────────────────────────────────────

get_type_hints(lambda x: x) # type: ignore

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(str.uppercase) # type: ignore
reveal_type(int.bit_length) # type: ignore

# ── Configuring the Python interpreter ──────────────────────────────────────

exec(open(os.devnull).read())

os.chdir("/path/to/new/directory")

os.system("ls -l")

# ── os.fsdecode ──────────────────────────────────────────────────────────────

str.decode(encoding="utf-8") # type: ignore
bytes.decode(encoding="latin-1") # type: ignore
open() # type: ignore
io.StringIO().write() # type: ignore

os.fsencode(b"hello world") # type: ignore
os.fsdecode("hello world".encode()) # type: ignore
os.path.basename(r"C:\Windows\system32\calc.exe").encode() # type: ignore

# ── path.expanduser ──────────────────────────────────────────────────────────

print(pathlib.Path.home())
print(pathlib.Path("~/Desktop").expanduser())

# ── pathlib.Path.cwd ─────────────────────────────────────────────────────────

pathlib.Path.cwd()

for directory in pathlib.Path("."):
    print(directory.name)

# ── pathlib.Path.is_absolute ─────────────────────────────────────────────────

pathlib.Path("/etc/hosts").is_absolute()
pathlib.Path("./.env").is_absolute()

# ── pathlib.Path.mkdir ───────────────────────────────────────────────────────

pathlib.Path.mkdir(exist_ok=True, parents=True)

# ── pathlib.Path.remove ──────────────────────────────────────────────────────

pathlib.Path.touch()
pathlib.Path.unlink()

# ── pathlib.Path.rename ──────────────────────────────────────────────────────

pathlib.Path.rename(new_pathlib.Path("new_file.txt"))

# ── pathlib.Path.rmdir ───────────────────────────────────────────────────────

pathlib.Path.rmdir()

# ── pathlib.Path.stat ────────────────────────────────────────────────────────

