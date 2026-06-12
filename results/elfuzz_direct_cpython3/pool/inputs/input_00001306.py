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

def example_typeddict() -> None:
    class Foo(TypedDict):
        bar: int
        baz: str

    f: Foo = {"bar": 123, "baz": "abc"}


def example_concatenate() -> None:
    class A:
        def do_something(self) -> str:
            return "A"

    class B:
        def do_something_else(self) -> str:
            return "B"

    class Foo(Generic[T], A):
        pass

    class Bar(Foo[B]):
        pass

    a: Foo[str] = Foo()
    assert a.do_something() == "A"


def example_annotated() -> None:
    class Foo(anio.Annotated[int]): ...
    class Bar(anio.Annotated[foo.Foo]): ...


anio: TypeAlias = Annotated


# ── Contextlib ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def example_contextmanager() -> tuple[int, list[int]]:
    yield 123, [456]


with example_contextmanager():
    print(reveal_type("ctx")) # type: ignore[arg-type]
    assert ctx == (123, [456])


@contextlib.contextmanager
async def example_async_contextmanager(x: int) -> AsyncIterator[int]:
    y: int = x * 10
    async with aio.Lock() as lock:
        try:
            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            raise ValueError(f"{x} is cancelled") from None
    yield y
    assert isinstance(y, int)


try:
    async for i in example_async_contextmanager(123):
        print(i)
except ValueError as e:
    print(e)
else:
    assert False



# ── Numbers (Abstract Base Classes) ──────────────────────────────────────────

# This example shows that the abstract base classes are used to provide an API
# which can be implemented by multiple concrete subclasses.
#
# This example also demonstrates how to use `numbers` ABCs and `typing.TypeVar`
# together.

# For more information about ABCs (abstract base classes) see:
# https://docs.python.org/3/library/abc.html#module-abc

# For more information about `typing.TypeVar`, see:
# https://mypy.readthedocs.io/en/stable/generics.html#generics-and-multiple-inheritance


class Number(numbers.Number): ...


assert Number.register(int) is True
assert Number.register(float) is True
assert Number.register(complex) is True
assert Number.register(Number) is True
assert Number.register(type(None)) is NotImplemented
assert Number.register(object()) is NotImplemented

Number.register(bool)
Number.register(str)

assert isinstance(True, Number)
assert isinstance(False, Number)
assert isinstance(17, Number)
assert isinstance(-42, Number)
assert isinstance(0o77, Number)
assert isinstance(0b11111111, Number)
assert isinstance(0xff, Number)
assert isinstance(0x1f, Number)
assert isinstance(0o1f, Number)
assert isinstance(0.b, Number)
assert isinstance(0.B, Number)
assert isinstance(0.f, Number)
assert isinstance(0.F, Number)
assert isinstance(0.x, Number)
assert isinstance(0.X, Number)


# ── pathlib ──────────────────────────────────────────────────────────────────

pathlib.Path.cwd()

# ── tempfile ────────────────────────────────────────────────────────────────

tempfile.mkdtemp(prefix="example")

# ── csv ────────────────────────────────────────────────────────────────────

csv.writer(io.StringIO())
csv.reader(io.StringIO())

# ── base64 ──────────────────────────────────────────────────────────────────

base64.encodebytes(b"hello world")
base64.decodebytes(base64.encodebytes(b"hello world"))

# ── hashlib ─────────────────────────────────────────────────────────────────

hashlib.sha256(b'hello world')
hashlib.sha256('hello world'.encode('utf8'))
hashlib.new('sha256', b'hello world')

# ── hmac ────────────────────────────────────────────────────────────────────

hmac.compare_digest(b'secret key', 'secret key')


# ── secrets ─────────────────────────────────────────────────────────────────

secrets.token_bytes(1024)
secrets.token_hex(1024)
secrets.token_urlsafe(1024)
secrets.randbits(1024)


# ── textwrap ────────────────────────────────────────────────────────────────

textwrap.indent("hello\nworld", "  ")

# ── string.Formatter ────────────────────────────────────────────────────────

str.format_map({"a": 123})

# ── string Formatter options ────────────────────────────────────────────────

'{:,}'.format(1000)
'{:+}'.format(1000)
'{:e}'.format(1000)
'{:.2f}'.format(1000)
'{:-#.2f}'.