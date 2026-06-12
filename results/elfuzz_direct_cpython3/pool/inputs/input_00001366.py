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


# ── class_typing ────────────────────────────────────────────────────────────

class MyClass:
    def _private_method(self) -> None:
        pass

    def public_method(self) -> None:
        self._private_method()


# ── classvar ────────────────────────────────────────────────────────────────

class SomeClass:
    count: ClassVar[int]
    value: ClassVar[int]

    def __init__(self) -> None:
        self.count += 1


some_class = SomeClass()
assert some_class.count == 1
SomeClass.value = 2
assert some_class.value == SomeClass.value
try:
    del SomeClass.count
except AttributeError as exc:
    assert isinstance(exc.__cause__, AttributeError)


# ── init_subclass ────────────────────────────────────────────────────────────

class Base:
    def __init_subclass__(
        cls,
        *args: P.args,
        **kwargs: P.kwargs,
        **extra_args: SomeType,
    ) -> None:
        super().__init_subclass__(*args, **kwargs)
        # ...


# ── class_getitem ────────────────────────────────────────────────────────────

T_co = TypeVar("T_co", covariant=True)
class MyCollection(Generic[T_co]):
    def __getitem__(self, item: int) -> T_co:
        return ...

    @classmethod
    def from_iterable(cls, items: Iterable[T_co]) -> MyCollection[T_co]:
        return ...


# ── abc numbers ──────────────────────────────────────────────────────────────

x = 3.879e-10
y = -4.2j
z = -1 + 2j
w = NotImplemented

print(isinstance(x, numbers.Real))  # True
print(isinstance(y, numbers.Complex))  # True
print(isinstance(z, numbers.Number))  # True
print(isinstance(w, numbers.Number))  # False
print(isinstance(1 << 80, numbers.Integral))  # True
print(isinstance(-1 >> 80, numbers.Integral))  # True
print(isinstance(float('inf'), numbers.Rational))  # False
print(isinstance(int, numbers.Integral))  # True
print(isinstance(bool, numbers.Number))  # True
print(isinstance(complex, numbers.Complex))  # True
print(isinstance(object(), numbers.Number))  # True


# ── pathlib ──────────────────────────────────────────────────────────────────

path_abc = pathlib.Path(__file__)
print(path_abc.is_absolute())  # True or False depending on current working dir.

print(path_abc.parent.parent.absolute())  # /Users/username/
print(path_abc.anchor)  # /

base_path = path_abc.parents[0]
print(base_path.relative_to("/"))  # /Users/username/

print(path_abc.resolve(strict=True).absolute())  # /Users/username/filename.py
print(path_abc.exists())
print(path_abc.is_file())

with open(path_abc, encoding="utf8") as file_obj:
    content = file_obj.read()

print(content.strip())


# ── tempfile ──────────────────────────────────────────────────────────────────

tempdir = tempfile.TemporaryDirectory()
filename = tempdir.name + "/file.txt"
with open(filename, mode="w") as file_obj:
    file_obj.write("Hello world!")

with open(filename, encoding="utf8") as file_obj:
    content = file_obj.read()

print(content.strip())

tempdir.cleanup()  # Delete the directory when Python exits.


# ── csv ──────────────────────────────────────────────────────────────────────

data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]

headers = ["name", "age"]

output_filename = "./test.csv"

with open(output_filename, mode="w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

read_data = []

with open(output_filename, mode="r", newline="") as csvfile:
        if inst is None:
            return self
        try:
            return getattr(inst, self.name)
        except AttributeError:
            if self.default is not None:
                setattr(inst, self.name, self.default)
