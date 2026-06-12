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
    username: str
    name:     str | None
    age:      int | None
    is_admin: bool | None

class Order:
    def __init__(self) -> None:
        self.items: list[tuple[int, int]] = []

    def __enter__(self) -> Order:
        return self

    def add(self, item_id: int, qty: int) -> None:
        self.items.append((item_id, qty))

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType) -> None:
        pass

def print_order(order: Order) -> None:
    for item_id, qty in order.items:
        print(f"{item_id} x {qty}")

with Order() as order:
    order.add(123_456, 2)
    order.add(888, 1)


# ── pathlib ──────────────────────────────────────────────────────────────────

path = pathlib.Path("/tmp/greetings.txt")
print(path.parent.name)
print(path.read_text(), end="") if path.exists else print("(no greetings)")

f = open(str(path), mode="a", encoding="utf-8")
f.write("\nHello world!")
f.close()
path.unlink()


# ── tempfile ────────────────────────────────────────────────────────────────

temp_path = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
temp_path.write("Greetings")
temp_path.seek(0)
print(temp_path.read())


# ── csv ────────────────────────────────────────────────────────────────────

# https://docs.python.org/3/library/csv.html
csv_file: Final[pathlib.Path] = pathlib.Path(__file__).parent / "data.csv"
csv_data: Final[list[list[str]]] = [
    ["id", "name"],
    [1, "Alice"],
    [2, "Bob"],
]
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in csv_data:
        writer.writerow(row)

with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(", ".join(row))


# ── Textwrap ────────────────────────────────────────────────────────────────

text_wrap: Finalbase64.b93decode(b"qQ==")
base64.b16decode("7E")
base64.b16encode(bytes(1))
base64.b16encode(bytes([1]))
base64.b16encode(bytearray(b"\x7e"))
base64.b16encode(memoryview(b"\x7e"))


# ── Hashlib ─────────────────────────────────────────────────────────────────

hashlib.md5(b"abc").hexdigest()


