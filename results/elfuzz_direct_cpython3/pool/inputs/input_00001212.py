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

record: UserRecord = {
    "id":            1,
    "name":          "Alice",
    "email":         "alice@example.com",
    "active":        True,
    "metadata":      {"age": 30},
}

print(record["name"])
print(UserRecord.__annotations__)

# ── ParamSpec ────────────────────────────────────────────────────────────────

def foo(x: T) -> T:
    ...

def bar(*args: List[int]) -> Tuple[int]:
    ...

p_foo: ParamSpec["Foo"] = ParamSpec("foo")
p_bar:  ParamSpec["Bar"] = ParamSpec("bar")
def baz(foo: p_foo.T, *bar: p_bar.args) -> p_foo.T:
    return foo + sum(bar)

# ── Annotated ────────────────────────────────────────────────────────────────

type Foo = Annotated[str, "this is a description"]
annotated: Foo = "hello"
print(annotated.description)

# ── get_type_hints ──────────────────────────────────────────────────────────

def foo(a: int, b: str, c: float=1.0) -> tuple[int, str, float]:
    pass


h = get_type_hints(foo)
print(h)


# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(1)
reveal_type([1])
reveal_type({"a": 1})
reveal_type((1,))
reveal_type(True)
reveal_type(None)
reveal_type(lambda x: x)
reveal_type(type(None))
reveal_type(object())
reveal_type(int)
reveal_type(str)
reveal_type(list)
reveal_type(frozenset)
reveal_type(set)
reveal_type(tuple)
reveal_type(dict)
reveal_type(range(10))
reveal_type(bytes)
reveal_type(bytearray)
reveal_type(memoryview)
reveal_type(slice)
reveal_type(frozenset)
reveal_type(float)
reveal_type(complex)
reveal_type(bool)
reveal_type(bytes)
reveal_type(bytearray)
reveal_type(io.BytesIO)
reveal_type(open("/path/to/file", "r"))
reveal_type(re.compile(r"abc"))
reveal_type(iter([1]))
reveal_type(next(iter([1])))
reveal_type(pow(2, 3))
reveal_type(hashlib.sha256())

reveal_type(ast.literal_eval("1"))              # pyright: ignore[reportGeneralTypeIssues]
reveal_type(ast.literal_eval('"abc"'))          # pyright:
    print(inspect.classmethod(Foo.bar))
    # <classmethod object at 0x7f8e9471cf90>

    params = [param for param in inspect.signature(Foo.bar).parameters.values()]
    print(params)
    # [<Parameter 'x'>]

    print(inspect.stack())
    # [(<frame at 0x7f8e9471e350>, <code object inspect_stack at 0x7f8e9471e2f0, file "<string>", line 1>, '<module>', 0, {'func': <function inspect_stack at 0x7f8e9471e2f0>})]

    parent_frame = inspect.currentframe().f_back
