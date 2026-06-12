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
assert isinstance(-17, Number)
assert isinstance(98.6, Number)
assert isinstance(-98.6, Number)
assert isinstance(0o17, Number)
assert isinstance(0o-17, Number)
assert isinstance(0b10001, Number)
assert isinstance(0b-10001, Number)
assert isinstance(0xABCDEF, Number)
assert isinstance(0x-ABCDEF, Number)

assert not isinstance("hello", Number)
assert not isinstance("", Number)
assert not isinstance(b"", Number)
assert not isinstance(bytearray(), Number)
assert not isinstance(memoryview(), Number)


assert issubclass(int, Number) is True
assert issubclass(float, Number) is True
assert issubclass(complex, Number) is True
assert issubclass(bool, Number) is True
assert issubclass(bytes, Number) is True
assert issubclass(bytearray, Number) is True
assert issubclass(memoryview, Number) is True
assert issubclass(Number, Number) is True
assert issubclass(type(None), Number) is False
assert issubclass(list, Number) is False



# ── pathlib ──────────────────────────────────────────────────────────────────

pathlib.Path.cwd()

p = pathlib.Path.home()
print(p