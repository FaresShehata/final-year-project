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

# ── class / decorator ────────────────────────────────────────────────────────

class MyFunction:
    def __call__(self, x: int) -> int:
        return x + 1


def add_one(x: int) -> int:
    return x + 1


# ── dataclasses ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int


def create_person(name: str, age: int) -> Person:
    return Person(name=name, age=age)


# ── functools ────────────────────────────────────────────────────────────────

def foo(*args: int, **kwargs: str) -> None:
    pass


def bar() -> None:
    foo(1, 2, 3, a=1, b=2, c=3)


# ── generator expressions ─────────────────────────────────────────────────────

# Yield from is the same as using yield inside of another generator.
async_generator = (
    value async for value in some_async_iterable if condition(value)
)


def generate_numbers(max_num: int) -> Generator[int, None, None]:
    """
    Generate a sequence of integers from 0 to `max_num - 1`.
    """

    for i in range(max_num):
        yield i


# ── inspect ──────────────────────────────────────────────────────────────────

def inspect_function(func: Callable[P, T]) -> None:
    print(inspect.getfullargspec(func))
    # inspect.signature(func).parameters.items()
    # inspect.Parameter('x', kind='positional-only')

    sig = inspect.signature(func)
    parameters = {name: param.kind.name for name, param in sig.parameters.items()}
    print(parameters)
    # {'a': 'keyword-only', 'b': 'var-positional', 'c': 'positional-only'}


def inspect_class(cls: type) -> None:
    print(inspect.getmro(cls))
    # (<class '__main__.Foo'>, <class 'object'>)

    print(inspect.getmembers(cls))
    # [('bar', <function Foo.bar at 0x7f8e9471dcd0>), ('foo', <function Foo.foo at 0x7f8e9471dc50>)]

    print(inspect.classmethod(Foo.bar))
    # <classmethod object at 0x7f8e9471cf90>

    params = [param for param in inspect.signature(Foo.bar).parameters.values()]
    print(params)
    # [<Parameter 'x'>]

    print(inspect.stack())
    # [(<frame at 0x7f8e9471e350>, <code object inspect_stack at 0x7f8e9471e2f0, file "<string>", line 1>, '<module>', 0, {'func': <function inspect_stack at 0x7f8e9471e2f0>})]

    parent_frame = inspect.currentframe().f_back
    print(parent_frame.f_code.co_filename)
    # '/home/username/workspace/codewarrior/seed_05.py'


def inspect_stack(level: int = 0) -> None:
    stack = inspect.stack()[level:]
    for frame_info in reversed(stack):
        print(frame_info)
        # (<frame at 0x7fe43f27f3d0>, <code object inspect_stack at 0x7fe43f27f350, file "/tmp/tmpy5tqjv2", line 1>, '<module>', 0, {})

        print((frame_info.frame,))
        # (<frame at 0x7fe43f27f3d0>,)

        print((frame_info.filename,))
        # '/tmp