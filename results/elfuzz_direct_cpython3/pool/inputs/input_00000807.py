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
    joined:  Seconds

# ── Function ────────────────────────────────────────────────────────────────────

async def main() -> None:
    """Python Tutorial — https://docs.python.org/3/library/threading.html"""


def sleep(seconds: Seconds) -> None:
    time.sleep(seconds)


def divide(numerator: int, denominator: int) -> float:
    print(f"{numerator} / {denominator}")
    return numerator / denominator


async def compute_square(number: int) -> int:
    await asyncio.sleep(1)
    return number**2


def read_file_lines(filename: str) -> Iterator[str]:
    with open(filename, encoding="utf-8") as file:
        yield from file.readlines()


async def read_file_async(filename: str) -> str:
    async with aiofiles.open(filename, mode="r", encoding="utf-8") as file:
        contents = await file.read()
    return contents


def write_string_to_file(string: str, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(string)


def prepend_lines(file_path: str, lines: Iterable[str]) -> None:
    with open(file_path, "rb+") as file:
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def write_numbers_to_file(numbers: Iterable[int], filename: str) -> None:
    with open(filename, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(numbers)


async def wait_for_seconds(seconds: Seconds) -> None:
    while seconds > 0:
        await asyncio.sleep(1)
        seconds -= 1


async def run_tasks_in_parallel(*tasks: Awaitable[Any]) -> None:
    tasks = [task for task in tasks if task is not None]
    await asyncio.gather(*tasks)


def find_files_with_extension(directory: PathLike, extension: str) -> List[Path]:
    paths = []
    for path in Path(directory).iterdir():
        if path.is_dir(): 
            paths.extend(find_files_with_extension(path, extension))
        elif path.suffix == extension:
            paths.append(path)
    return paths


def read_and_sort_users(filepath: PathLike) -> List[UserRecord]:
    users = []
    with open(filepath, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_record = {}
            for        self.counter[key] += count
        if len(self.counter) > self.max_size:
            rv = sorted([(self.counter[k], k) for k in self.counter],
                        reverse=True)[:self.max_size]
            del self.counter[self.counter.keys()[rv[-1][1]]]


# ── Slots ──────────────────────────────────────────────────────────────────────

class PersonProto:
    name: str
    age: int
    height: float
    weight: float

    def __repr__(self) -> str:
        return f"Person(name={self.name}, age={self.age})"

class Person(PersonProto, metaclass=dataclasses.DataClassMeta):
    __slots__: ClassVar[tuple[str, ...]] = ()

person_proto = PersonProto(name='John', age=30, height=1.75, weight=68.0)
print(person_proto)

p = Person(name='Jane', age=29, height=1.65, weight=70.0)
printdef ctypes_demo():
    a_addr = id(C())
    c = A.from_address(a_addr)

    # Unpack fields in native format to check they're the same as the original.
    assert a_addr == c.x
    assert c.y[0] == ord("A")

    for base in [A, B, C]:
        assert base._fields_
        assert not any(len(f[1]) > 1 for f in base._fields_)
        assert hasattr(base, "_anonymous_") is False
        assert hasattr(base, "_bitfield_") is False


def struct_demo():
    class A(struct.Struct):
        _fields_ = [("x", "i"),
                    ("y", "c", 2)]
    
    assert A.sizeof == 5   # 4 bytes for x, 2 bytes for y
    
    a = A.pack(-1, b"\0\0")
    a = A.unpack(a)
    assert a[0] == -1
    assert a[1] == b"\0\0"
    
    assert len(a) == 5       # actually returns tuple of unpacked values


# ── Array ─────────────────────────────────────────────────────────────────────

arr = array.array('h')
print(arr.typecode)  # 'h'
arr.append(1)
arr.extend([2, 3])
print(arr.tolist()) 