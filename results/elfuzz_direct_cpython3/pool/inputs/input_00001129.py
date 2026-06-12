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
from types import TracebackType
from typing_extensions import LiteralString, Self

T = TypeVar("T")
P = ParamSpec("P")


def example_thread():
    t = threading.Thread(target=time.sleep, args=[2])
    t.start()


async def example_coroutine() -> None:
    await asyncio.sleep(2)


def example_concurrent_futures_executor():
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = list(executor.map(lambda x: math.cos(x), range(-3, 3)))

# ── String Parsing ───────────────────────────────────────────────────────────

parsed_string = ast.parse('print("Hello World")')
tokens = tokenize.tokenize(io.BytesIO(b"Print Hello World").readline)

# ── Typing Extras ────────────────────────────────────────────────────────────

example_typed_dict = {
    "name": str,
    "age": int,
}
example_classvar = ClassVar[int]
example_literalstring = LiteralString


class ExampleClass(NamedTuple):
    name: str
    age: int


example_namedtuple = ExampleClass(name="John Doe", age=30)


example_typeddict = TypedDict(
    'ExampleTypedDict',
    {"name": str},
    total=False,
)
example_typedef = TypeAlias[str, int]


class ExampleClassWithTypingExtras(Generic[T]):
    value: T
    optional_value: Annotated[
        T | None, 
        "This is an optional field",
    ] = None


class ExampleParamSpec(ParamSpec["P"]):
    ...


def example_function_with_param_spec(*args: P.args, **kwargs: P.kwargs) -> None:
    pass


def example_contextmanager() -> Iterator[None]:
    yield


async def example_async_contextmanager(n: int) -> Iterable[int]:
    yield from [i for i in range(n)]


with example_contextmanager(), <|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>try:
    async for i in example_async_contextmanager(123):
        print(i)
except ValueError as e:
    print(e.args[0]) # type: ignore[attr-defined]

# ── Numbers ABC ─────────────────────────────────────────────────────────────-

assert isinstance(math.pi, numbers.Real)
assert isinstance(math.inf, numbers.Number)

# ── Pathlib ─────────────────────────────────────────────────────────────────

p1 = pathlib.Path("a.txt")
assert isinstance(p1.name, str)
assert p1.name.endswith(".txt")

# ── Tempfile ────────────────────────────────────────────────────────────────

temp_dir = tempfile.TemporaryDirectory()
print(temp_dir.name)

# ╰─ DirectoryNotFoundError: Device or resource busy (errno=16)
