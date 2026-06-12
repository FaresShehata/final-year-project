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

# ── ParamSpec ────────────────────────────────────────────────────────────────

Params = ParamSpec("Params")


class User(NamedTuple):
    username: str
    password: str


UserFunc = Callable[params, result]


def validate_password(user: User, password: str) -> None:
    if user.password != hash_password(password): raise ValueError("invalid password")


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


# ── ClassVar ────────────────────────────────────────────────────────────────

class BaseClass:

    _shared_state: ClassVar[dict[str, Any]] = {"_value": 0}

    @classmethod
    def _get_shared(cls) -> ClassVar[dict[str, Any]]:
        return cls._shared_state

    @classmethod
    def _reset_shared(cls) -> None:
        cls._shared_state.clear()

    @property
    def value(self) -> int:
        return self._get_shared()["_value"]

    @value.setter
    def value(self, new_value: int) -> None:
        self._get_shared()["_value"] = new_value


class Child(BaseClass):

    @classmethod
    def _get_shared(cls) -> ClassVar[dict[str, Any]]:
        return cls._shared_state


Child()._reset_shared()

b = BaseClass()
c = Child()

print(f"{b.value=}")            # b.value=0
print(f"{c.value=}")            # c.value=0
BaseClass._reset_shared()
print(f"{b.value=}")            # b.value=0
print(f"{c.value=}")            # c.value=0

b.value = 1
c.value = 2
print(f"{b.value=}")            # b.value=1
print(f"{c.value=}")            # c.value=2
BaseClass._reset_shared()
print(f"{b.value=}")            # b.value=0
print(f"{c.value=}")            # c.value=0


# ── Annotated ───────────────────────────────────────────────────────────────

ANONYMOUS: Annotated[str, 'Anonymous'] = "anonymous"

# ── ParamSpec ───────────────────────────────────────────────────────────────

class MyFunction(Generic[T]):
    def __call__(self, arg: T) -> T:
        ...


foo = MyFunction[int]()
bar# Comprehension example
[(x, y) for x in range(3) for y in range(2)]
[(x, y) for x in range(3)]  # <- only one `y` iteration possible


# Generator expression example
generator_expression = (x ** 2 for x in range(3))
next(generator_expression)  # 0
next(generator_expression)  # 1
next(generator_expression)  # 4
next(generator_expression)  # StopIteration exception


def count_to(limit: int) -> Iterator[int]:
    current_number = 0
    while current_number < limit:
        yield current_number
        current_number += 1


count_generator = count_to(5)
for number in count_generator:
    print(number, end=" ")  # 0 1 2 3 4
    assert next(count_generator) == 5


# Generator example
def fibs() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


fibs_generator = fibs()

assert next(fibs_generator) == 0
assert next(fibs_generator) == 1
assert next(fibs_generator) == 1
assert next(fibs_generator) == 2
assert next(fibs_generator) == 3
assert next(fibs_generator) == 5


# Coroutine example
async def main():
    async with (
        StreamReader() as reader,
        StreamWriter() as writer,
    ):
        task = asyncio.create_task(reader.read_until(b"q"))
        writer.write("hello".encode())

        _, data = await asyncio.gather(task, writer.drain())
        assert data.decode().strip() == "hello"
        print("done.")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        loop.close()


class StreamReader(object):
    pass


class StreamWriter(object):
    pass


async def test_main():
    async with (
        StreamReader() as reader,
        StreamWriter() as writer,
