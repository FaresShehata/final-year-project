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


def metrics_record(
        latency_ms: float,
        throughput: float,
        error_rate: float) -> MetricsRecord:
    """Construct a new metrics record."""
    return {
            "latency_ms": latency_ms,
            "throughput": throughput,
            "error_rate": error_rate,
           }


# ── class GetItem ────────────────────────────────────────────────────────────

_T1 = TypeVar("_T1")
class GetItem(Generic[_T1]):
    def __getitem__(self, index: int | slice) -> _T1:
        ...

    def __iter__(self) -> Iterator[_T1]:
        ...

    def __len__(self) -> int:
        ...


class A(GetItem[int]):
    pass


class B(GetItem[float]):
    pass


assert issubclass(A, GetItem)
assert not issubclass(B, GetItem)


class C(GetItem[int | float]):
    pass


assert isinstance(C(), GetItem)
assert issubclass(C, GetItem)


class D(GetItem[int | float | str]):
    pass


assert isinstance(D(), GetItem)
assert issubclass(D, GetItem)


# ── class SetItem ────────────────────────────────────────────────────────────

_T2 = TypeVar("_T2")


class SetItem(Generic[_T2]):
    def __setitem__(self, index: int | slice, value: _T2) -> None:
        ...

    # def __delitem__(
    #         self, index: int | slice) -> None:
    #     ...


class E(SetItem[str]):
    pass


assert issubclass(E, SetItem)


class F(SetItem[int | str]):
    pass


assert isinstance(F(), SetItem)
assert issubclass(F, SetItem)


class G(SetItem[int | str | bytes]):
    pass


assert isinstance(G(), SetItem)
assert issubclass(G, SetItem)


# ── class Repr ───────────────────────────────────────────────────────────────

class PersonRepr(str):
    def __new__(cls, first: str, last: str) -> PersonRepr:
        return super().__new__(cls, f"{first} {last}")

    def __str__(self) -> str:
        return f"Person({super().__repr__()})"

    def __repr__(self) -> str:
        return f"<{super().__repr__()}>"


class