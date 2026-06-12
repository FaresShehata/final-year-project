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


UserKeys: TypedDict = {
    "id":   int,
    "name": str,
}


# ── ParamSpec ────────────────────────────────────────────────────────────────

def func(**kwargs: type[Any]):
    ...


ParamSpecKwargs: ParamSpec["Kwargs"]


def func(**kwargs: Kwargs) -> None:
    ...


func(name=str, age=int)


# ── GetTypeHints ────────────────────────────────────────────────────────────

def get_type_hints_with_annotations(func: Callable[P, T]) -> dict[str, type[Any]]:
    return get_type_hints(func, globalns=func.__globals__)


get_type_hints_with_annotations(get_type_hints_with_annotations)
# {'func': <class 'function'>}

# ─── RevealType Stub ────────────────────────────────────────────────────────

reveal_type(123)
reveal_type("hello world")
reveal_type([1, 2, 3])
reveal_type(UserRecord())
reveal_type(UserKey(name=str))

reveal_type(str.split())
reveal_type((lambda x: True)(x))
reveal_type(lambda x: x + 1(x))


# ── ContextLib ──────────────────────────────────────────────────────────────

with open(pathlib.Path(__file__)) as f:
    print(f.read())

print()

with contextlib.redirect_stderr(None) as stderr:
    print(stderr.getvalue())
    print('Hello, World!')


# ── Numbers ABC ─────────────────────────────────────────────────────────────

assert isinstance(1.0 * 1.0, numbers.Real)
assert isinstance(-0.0, numbers.Number)
assert not isinstance(object(), numbers.Real)
assert not isinstance([], numbers.Number)

# ── Pathlib ─────────────────────────────────────────────────────────────────

pathlib.Path.cwd()
pathlib.PurePath("/usr/bin") / pathlib.PurePath("ls")


# ── Tempfile ───────────────────────────────────────────────────────────────

tempfile.gettempdir()
tempfile.TemporaryDirectory(prefix="my-unique-prefix", dir=tempfile.gettempdir())


# ── CSV ────────────────────────────────────────────────────────────────────

csv.writer(io.StringIO()).writerow(["foo", "bar"])
csv.reader(io.StringIO("spam,bagel\neggs,milk")).__next__()
list(csv.DictReader(io.StringIO("foobar\nbazquux")))



# ── Base64 ─────────────────────────────────────────────────────────────────

base64.b85decode(b"qQ==")
base64.b93decode(b"qQ==")
base64.b16decode("7E")
base64.b16encode(bytes(1))
base64.b16encode(bytes([1]))
base64.b16encode(bytearray(b"\x7e"))
base64.b16encode(memoryview(b"\x7e"))


# ── Hashlib ─────────────────────────────────────────────────────────────────

hashlib.md5(b"abc").hexdigest()


# ── HMAC ───────────────────────────────────────────────────────────────────

hmac.new(key=b"a", msg=b"b", digestmod=hashlib.sha256).digest()


# ── Secrets ─────────────────────────────────────────────────────────────────

secrets.token_bytes(100)
secrets.token_hex(100)
secrets.token_urlsafe(100)


# ── String ──────────────────────────────────────────────────────────────────

string.capwords("Foo bar baz", separator="_")

textwrap.indent("foo", "> ")
text