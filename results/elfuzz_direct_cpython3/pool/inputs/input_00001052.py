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


# ── contextlib ───────────────────────────────────────────────────────────────


@contextlib.contextmanager
def timer():
    start_time = time.time()
    yield lambda: time.time() - start_time
    print('Elapsed:', end=' ')
    print(timer())


with timer() as elapsed:
    time.sleep(3.5)
    print(elapsed())


# ── numbers ─────────────────────────────────────────────────────────────────


x = 123_456_789
assert x // 1 == x
assert x % 1 != 0
