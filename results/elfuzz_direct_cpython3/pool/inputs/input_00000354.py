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


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class CheckedAnnotated(Annotated[T, ..., str]):
    def __get__(self, instance: object, owner: type[Any]) -> T:
        return super().__get__(instance, owner)[1:] if instance else self.__args__[1:]

class StrCheckedAnnotated(CheckedAnnotated[str]): ...

class FloatCheckedAnnotated(CheckedAnnotated[float]): ...

class IntCheckedAnnotated(CheckedAnnotated[int]): ...

class NegIntCheckedAnnotated(IntCheckedAnnotated): ...

class PosIntCheckedAnnotated(IntCheckedAnnotated): ...

class NonZeroIntCheckedAnnotated(PosIntCheckedAnnotated): ...

class PredicateCheckedAnnotated(Predicate, Annotated[Predicate, "predicate"]): ...

# ── Annotated constraint violations (type checking only) ──────────────────────
FloatCheckedAnnotated(False)
PosIntCheckedAnnotated(-2.33)
NegIntCheckedAnnotated(2)
NonZeroIntCheckedAnnotated(0)


# ─────────────────────────────────────────────────────────────────────────────

def swap(a: int, b: int) -> tuple[int, int]:
    return b, a
swap(1, 2)

# ── Strings and bytes ────────────────────────────────────────────────────────


def decode_bytes(s: bytes, encoding: str = "utf-8") -> str:
    try:
        return s.decode(encoding)
    except UnicodeError as e:
        raise ValueError(f"invalid {encoding} data") from e
decode_bytes(b'abc')

# ── String formatting ────────────────────────────────────────────────────────

str.format("{name}, {active?}")
'{name}, {active?}'.format(name='John', active=True)

# ── String interpolation ──────────────────────────────────────────────────────

print(
    f"{name=}",
    f"{name=} {active=!r}"
)

# ── Tokenize ────────────────────────────────────────────────────────────────


tokenize.tokenize(io.BytesIO(b'foo bar\n').readline)

for token in tokenize.generate_tokens(io.StringIO('1 + 2').readline):
    print(token.type, token.string, token.start, token.end, token.line)

# ── Text wrap ────────────────────────────────────────────────────────────────


textwrap.fill('Hello\nWorld!', width=70)

# ── String formatter characters ─────────