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
    # metrics always have a timestamp field
    timestamp: datetime.datetime
    
    # metrics may have any number of other fields
    [str]:      Any


class MetricName(str, Enum):
    value           = "value"           # metric value for the given key
    count           = "count"           # number of times this metric has been recorded
    sum             = "sum"             # sum of all values
    min             = "min"             # minimum value
    max             = "max"             # maximum value
    mean            = "mean"
    std_dev         = "std_dev"

    
MetricInfo: TypedDict = {
    MetricName.count:    {"type": "integer", "description": "number of times this metric has been recorded."},
    MetricName.sum:      {"type": "float",   "description": "sum of all values"},
    MetricName.min:      {"type": "float",   "description": "minimum value"},
    MetricName.max:      {"type": "float",   "description": "maximum value"},
    MetricName.mean:     {"type": "float",   "description": "average value"},
    MetricName.std_dev:  {"type": "float",   "description": "sample standard deviation"},
}

MetricSchema: TypedDict = {
    str:                  MetricInfo,
    ...                  :{"type":"string"}
}

# ── Defining Functions ───────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    """add two integers together"""
    return a + b


def multiply(a: int, b: int) -> int:
    """multiply two integers together"""
    return a * b


class Incrementor(Generic[T]):
    """an object that can increment its internal state and retrieve it"""

    def __init__(self, initial: T = 0) -> None:
        self._state: T = initial

    @property
    def state(self) -> T:
        """public getter method to access the current state"""
        return self._state
    
    def increment(self, delta: int = 1) -> None:
        """increment by delta. accepts negative values"""
        if isinstance(delta, int):
            self._state += delta
        else:
            raise TypeError(f"{delta} is not an integer")


def is_even(num: int) -> bool:
    """determines whether num is even or odd"""
    return True if num % 2 == 0 else False


def make_hash(key: bytes, data: bytes) -> str:
    """hashes data using key"""
    return hashlib.blake2b(key=key, data=data).hexdigest()

  
def xor(a: int, b: int) -> int:
    """xor two integers together"""
    return a ^ b


def power(base: int, exponent: int) -> int:
    """raises base to the exponent power"""
    return base ** exponent


def divide(dividend: float, divisor: float) -> float:
    """divides dividend by divisor. returns zero on division by zero."""
    try:
        result = dividend / divisor
    except ZeroDivisionError:
        result = 0
    finally:
        return result
    
    
def parse_csv(csv_data: str, delimiter: str = ",") -> tuple[list[tuple[str, ...]], list[tuple[int, ...]]]:
    """parses csv data into rows and columns"""
    parsed_rows: list[tuple[str, ...]] = []
    
    reader = csv.reader(io.StringIO(csv_data), delimiter=delimiter)
    for row in reader:
        parsed_rows.append(tuple(row))
        
    return parsed_rows
    

# ── Classes ─────────────────────────────────────────────────────────────────-

class Counter(Generic[T], Generic[T]):
    """counts items from initial value"""


class Hash    def hash(self, data: bytes) -> str:
        return base64.b64encode(data).decode()
    

class Sha256Hash(Base64Hash):
    """hashes data using sha-256 with hexdigest encoding"""

    def hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

        
class HmacSHA256Hash(Sha256Hash):
    """hashes data using hmac-sha256 with base64 encoding."""

    def __init__(self, key: bytes) -> None:
        self._key = key
        
    def hash(self, data: bytes) -> str:
        return hmac.new(self.key.encode(), msg=data, digestmod=hashlib.sha256).hexdigest()


def generate_hex_key() -> str:
    """generates a random hexadecimal key."""
    return secrets.token_hex(32)


def