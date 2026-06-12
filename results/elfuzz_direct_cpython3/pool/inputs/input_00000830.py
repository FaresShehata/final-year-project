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


# ── RevealType ───────────────────────────────────────────────────────────────

reveal_type(2.3)         # >>> Revealed type is 'float'
reveal_type(None)        # >>> Revealed type is 'None'
reveal_type(True)        # >>> Revealed type is 'builtins.bool'
reveal_type('hello')     # >>> Revealed type is 'builtins.str'

reveal_type([1, 2, 3])   # >>> Revealed type is 'list[builtins.int]'
reveal_type({1, 2, 3})   # >>> Revealed type is 'set[builtins.int]'
reveal_type((1, 2, 3))   # >>> Revealed type is 'tuple[builtins.int]'
reveal_type(range(10))   # >>> Revealed type is 'generator[int, None, None]'
reveal_type(io.StringIO())  # >>> Revealed type is 'io.TextIOWrapper[str]'


# ── Annotated, get_type_hints ────────────────────────────────────────────────

def f(x: Annotated[float, "f"], y: Annotated[str, "s"]) -> Annotated[float, "g", "h"]:
    pass

print(get_type_hints(f, globalns={"Annotated": Annotated}))  # {'x': <class 'builtins.float'>, 'y': <class 'builtins.str'>}


# ── functools.partial ────────────────────────────────────────────────────────

from functools import partial

add_2 = partial(sum, start=2)
assert add_2([1, 2, 3]) == 7


# ── functools.lru_cache ──────────────────────────────────────────────────────

from functools import lru_cache
import math

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fib(n - 2) + fib(n - 1)

print(fib(8))
# >>> 21

# Clear the cache before next run -----------------------------

fib.cache_clear()
print(fib(9))
# >>> 34


# ── functools.wraps ─────────────────────────────────────────────────────────

from functools import wraps

def decorator(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args:    return not even_tc(n)


# ── Higher-order functions, list comprehensions, and generators ───────────────

def map_v1(fn: Callable[[Any], Any], xs: Iterable[Any]) -> list:
    return list(map(fn, xs))


