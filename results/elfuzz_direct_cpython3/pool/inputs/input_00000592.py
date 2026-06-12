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

@contextlib.contextmanager
def suppress(*types, **exc_info) -> Generator[None, None, None]:
    yield


with suppress(AttributeError):
    raise AttributeError()


@contextlib.redirect_stdout(io.StringIO())
def do_print() -> str:
    print("Hello World!")
    assert False, "Should not reach here."


do_print()
output = do_print().strip()
assert output == "", repr(output)

# ── Numbers ────────────────────────────────────────────────────────────────

if isinstance(1.0e0, numbers.Number):
    pass

if isinstance(1j, numbers.Complex):
    pass

if isinstance(-0.0, numbers.Real):
    pass

if isinstance(int(), numbers.Integral):
    pass

if isinstance(float(), numbers.Real):
    pass

if isinstance(complex(), numbers.Complex):
    pass

if isinstance(bool(), numbers.Number):
    pass

if isinstance(None, numbers.Number):
    pass

if isinstance(object(), numbers.Number):
    pass

if isinstance(type(None), numbers.Number):
    pass

if isinstance(type(object()), numbers.Number):
    pass

# ── Pathlib ─────────────────────────────────────────────────────────────────

path = pathlib
def _annotated_get_args(annotated: type[Any]) -> tuple[type[Any], ...]:
    origin = getattr(annotated, "__origin__", object)

    if origin != Annotated:
        raise ValueError("Must be an 'Annotated' type.")

   