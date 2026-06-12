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
    """Test is_palindrome()."""

    results = []
    for length in range(1, 51):
        n_tests = 5 * pow(length, 4)
        count = 0
        for _ in range(n_tests):
            s = "".join(secrets.choice(string.ascii_lowercase) for _ in range(length))
            if is_palindrome(s):
                count += 1

        results.append((length, count / n_tests))

    return results


# ── Predicate ────────────────────────────────────────────────────────────────

def filter_even(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number % 2 == 0]


def filter_odd(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number % 2 != 0]


def increment(nums: list[int]) -> list[int]:
    return [num + 1 for num in nums]


def decrement(nums: list[int]) -> list[int]:
    return [num - 1 for num in nums]


def negate(nums: list[int]) -> list[int]:
    return [-num for num in nums]


def square(nums: list[int]) -> list[int]:
    return [num**2 for num in nums]


def cube(nums: list[int]) -> list[int]:
    return [num**3 for num in nums]


# ── Function ─────────────────────────────────────────────────────────────────

def show_table(rows: list[list[str]]) -> None:
    col_widths = [max(map(len, column)) for column in zip(*rows)]
    fmt = "{:" + " ".join(["<"+str(col_width)+""]*len(rows[0]))+"}\n"
    for row in rows:
        print(fmt.format(*row))


def rotate_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


def find_first(iterable: Iterable[Any], predicate: Predicate) -> tuple[Any, ...]:  # noqa: E741
    """
    Return the first element that satisfies the predicate.

    If no such element exists, raise StopIteration exception.
    """

    try:
        yield next(filter(predicate, iterable))
    except StopIteration:
        raise ValueError("No element found.")


def flatten(seq: Sequence[Sequence[T]] | list[tuple[T, ...]]) -> list[T]:
    return list(itertools.chain.from_iterable(seq))


def transpose(mtx: list[list[T]]) -> list[list[T]]:
    return list(zip(*mtx))


def transpose_2d(table: list[list[int]]) -> list[list[int]]:
    return [*zip(*(list(itertools.islice(row, i, len(table))) for i in range(len(table[0]))) for row in table)]

# ──Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          decorators, context managers
"""


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm for greatest common divisor."""
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:  # a < b
            b %= a

    return max(a, b)


@gcd
def find_gcd(*numbers: int) -> int:
    """Find greatest common divisor of several integers."""

@gcd
def list_gcd(list_of_numbers: list[int]) -> int:
    """Calculate GCD of all numbers in the list."""


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()