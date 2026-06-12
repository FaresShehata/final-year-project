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
    first:    str
    last:     str
    gender:   Literal["M", "F"]
    email:    str | None
    ip_address: str | None
    joined:   Seconds

def user_record_to_str(record: UserRecord) -> str:
    return f"{record['id']} {record['first']}{record['last']:>10} {record.get('gender', ''):>3}"

# ── ParamSpec ────────────────────────────────────────────────────────────────

def log_each(f: Callable[P, T]) -> Callable[..., T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        result = f(*args, **kwargs)
        print(f"{' '.join(str(arg) for arg in args)} {' '.join(f'{k}={v}' for k,v in kwargs.items())}")
        print(f"result: {result}\n")
        return result

    return wrapper


def is_palindrome(s: str) -> bool:
    """Return whether the given string s is a palindrome."""

    l = len(s)
    if l % 2 == 0:
        # Odd number of letters.
        mid = l // 2
        return all([s[i] == s[l - i - 1] for i in range(mid)])
    else:
        # Even number of letters.
        mid = l // 2 + 1
        return all([s[i] == s[mid - i] for i in range(mid)])


@log_each
def test_is_palindrome() -> tuple[int, ...]:
    """Test the is_palindrome function with different strings."""
    return tuple(is_palindrome(s) for s in ("a", "", "aa", "abba", "abc"))


def parse_csv(file_path: pathlib.Path) -> list[list[str]]:
    """
    Parse a CSV file and return a list of rows.

    Each row is represented as a list containing the values from that row.
    """

    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]
    return data


def find_sum_of_columns(data: list[list[str]]) -> list[tuple[int, int, int]]:
    """
    Find the sum of columns in the given list of rows.

    Returns a list of tuples where each tuple contains the column number, the
    minimum value in that column, and the maximum value in that column.
    """

    col_min = []
    col_max = []
    for i in range(len(data[0])):
        col_data = [float(row[i]) for row in data]
        min_val = min(col_data)
        max_val = max(col_data)
        col_min.append(min_val)
        col_max.append(max_val)
    out = [(i+1, col_min[i], col_max[i]) for i in range(len(col_min))]
    return out


# ── Annotated ────────────────────────────────────────────────────────────────

def add(a: 'Annotated[int, "positive"]', b: 'Annotated[int, "positive"]') -> int:
    """Add two positive integers."""

    return a + b


def get_type_hint(name: str) -> tuple[type[Any], str]:
    """Get the type hint for a variable or parameter."""

    ty = get_type_hints(add)["b"]
    name = ty.__name__
    return ty, name


def print_type_hint(ty: type[Any]) -> None:
    """Print the type hint for a variable or parameter."""

    print(f"type hints for {ty}: ", end="")
    for item in get_type_hints(ty).items():
        print(item, end=", ")
    print("\b \b")


# ── get_type_hints ──────────────────────────────────────────────────────────

def get_another_type_hint(ty: type[Any]) -> str:
    """Get another type hint for a variable or parameter."""

    return