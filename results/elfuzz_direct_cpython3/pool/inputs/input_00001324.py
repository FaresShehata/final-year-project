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

TRandomAccessIterable       : TypeAlias = "collections.abc.Sequence[T] | collections.abc.MutableSequence[T]"
TRandomAccessIterator      : TypeAlias = "collections.abc.Iterator[T] | collections.abc.AsyncGenerator[T, S]"
TRandomAccessIterableOrStr : TypeAlias = "TRandomAccessIterable | str"
TRandomAccessIteratorOrStr: TypeAlias = "TRandomAccessIterator | str"

# ── Typing Extras ───────────────────────────────────────────────────────────-

F: Final[FloatingNumber] = 1.234
S: Final[StringLike]     = "String!"
c: Final[Complex]        = 3 + 4j
d: Final[BytesLike]      = b"Hello!"
i: Final[Integral]       = 789_123_456
o: Final[Octal]          = 0o123_456
h: Final[Hexadecimal]    = 0xABC_def
u: Final[UppercaseHexadecimal] = 0XABCD_EF
s: Final[ByteString]     = b"\xc3\xbc\xc3\xa4\xe2\x82\xac"
b: Final[Boolean]        = True
n: Final[Numeric]        = -123_456
r: Final[Rational]       = Fraction(7, 12)
t: Final[Tuple[int, float]] = (1,)
u: Final[tuple[str, int]] = ("", 1)
v: Final["tuple"] = ()
w: Final[tuple[Any, ...]] = (True,)
x: Final[list[int]] = [1]
y: Final[list[float]] = []
z: Final[list] = []

class Foo:
    x: int
    y: float
    z: str

a: Final[Foo] = Foo()

def f(x: int) -> None:
    pass


def g(*args: int, **kwargs: float) -> None:
    pass


def h(**kwargs: complex) -> None:
    pass


class I(Generic[T]):
    a: T
    b: T
    c: T
    d: T
    e: T
    f: T
    g: T
    h: T
    i: T
    j: T
    k: T
    l: T
    m: T
    n: T
    o: T
    p: T
    q: T
    r: T
    s: T
    t: T
    u: T
    v: T
    w: T
    x: T
    y: T
    z: T

Foo.__annotations__.update({
    "x": int,
    "y": float,
    "z": str,
})

I.__parameters__.update({
    "T": int,
})
I.update_forward_refs(T=float)

def _get_annotations(cls: type):
    return cls.__dict__["__annotations__"]

def _test_incomplete_annotation(cls: type) -> bool:
    try:
        return len(get_type_hints(cls)) != len(_get_annotations(cls))
    except TypeError:
        return False

if not _test_incomplete_annotation(I) and \
   not _test_incomplete_annotation(Foo): print("incomplete annotation")

for t in range(-2**32-1, 2**    t: collections.abc.Sequence[T],
    u: collections.abc.Set[T],
