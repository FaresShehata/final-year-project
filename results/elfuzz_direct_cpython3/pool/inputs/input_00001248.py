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
R  = RevealType[T]
S  = SupportsIndex | SupportsFloat
Seconds   : Final[Literal[1]] = 1
Milliseconds: Final[Literal[0.001]] = 0.001


def get_execution_time(
    func: Callable[P, R],
    *args: P.args,
    **kwargs: P.kwargs
) -> tuple[R, Seconds]:
    start_time: float = time.perf_counter()
    result: R = func(*args, **kwargs)
    end_time: float = time.perf_counter()

    return result, end_time - start_time


class Counters(Generic[T]):
    def __init__(self) -> None:
        self.counts: dict[int, T] = {}

    def increment(self, key: int) -> None:
        if key in self.counts:
            self.counts[key] += 1
        else:
            self.counts[key] = 1

    def decrement(self, key: int) -> None:
        if key not in self.counts or self.counts[key] == 0:
            raise ValueError(f"Key {key} does not exist.")

        self.counts[key] -= 1


class CounterGroup(Counters[Any]):
    pass


class CounterSet(CounterGroup):
    pass


class CyclicCounterGroup(CounterGroup):
    def __iter__(self) -> Iterable[int]:
        for i in itertools.cycle(range(len(self))):
            yield i


class CyclicCounterSet(CyclicCounterGroup):
    pass


class CyclicCounterMap(map):
    def __getitem__(self, key: int) -> int:
        try:
            return super().__getitem__(key)
        except KeyError:
            return next(iter(x for x in itertools.cycle(super().keys()) if x > key))


class Sentinel(int):
    pass


if False:
    from mypy_extensions import TypedDict  # noqa:F401
else:
    class Foo(TypedDict):
        a: int
        b: str


# ── __class_getitem__ ────────────────────────────────────────────────────────

class A(Generic[T]):
    @classmethod
    def __class_getitem__(cls, params: tuple[T]) -> A[T]:
        ...


# ── __set_name__() ──────────────────────────────────────────────────────────


class B:

    def __set_name__(self, owner, name):
        self.name = name
        print(owner, name)


b = B()
print(b.name)


# ── __init_subclass__() ──────────────────────────────────────────────────────


class C:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        ...


C()


# ── contextlib (AbstractContextManager) ──────────────────────────────────────


@contextlib.contextmanager
def open_file(filename: str, mode: Literal["r", "w"]) -> Iterator[str]:
    f = open(filename, mode=mode)
    try:
        yield f.read()
    finally:
        f.close()


with open_file("./test.txt", mode="r") as file:
    print(file)


@contextlib.contextmanager
def suppress(*exceptions):
    """Suppress any exception that matches the given exceptions."""
    try:
        yield
    except exceptions:
        pass


@contextlib.contextmanager
def redirect_stdout(stream):
    """Redirect stdout to another stream while within this context."""
    old_stream = sys.stdout
    sys.stdout = stream
    try:
        yield stream
    finally:
        sys.stdout = old_stream


# ── numbers ABC ──────────────────────────────────────────────────────────────

numbers.Number.__mro__
float.__add__.__mro__

i = 23
i == 23
i is 23
i + 23
i + 23j
i**2
i.bit_length()
i.conjugate()
i.from_bytes(bytearray([1, 2, 3]), 'little')
i.is_integer()
i.real
i.imag

x = complex(i)
y = real(x)
z = imag(x)

a = x + y + z

a
a - b
a**2
abs(a)
max(a, b, c, d)
min(a, b, c, d)
pow(a, b, c)
round(a, n)
int(a), long(a), float(a), complex(a)
complex(real(x), imag(y))
divmod(x, y)
list(map(pow, [x], range(8)))
sorted([x, y])
sum((x, y))
any([True, False, True])
all([False, True, False, True])

bool(x), bool(y), bool(z)
type(x), type(y), type(z)
hash(x), hash(y)
tuple(map(hash, [x, y]))
len(x), len(y)
id(x), id(y)
bin(x), oct(x), hex(x)
octal(x), hexadecimal(x), binary(x)
dir(x), dir(y)
str(x), repr(x)
format(x)
isinstance(x, numbers.Complex)
