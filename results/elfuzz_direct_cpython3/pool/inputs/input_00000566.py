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
def test_is_palindrome() -> None:
    assert is_palindrome("")           == True
    assert is_palindrome("a")          == True
    assert is_palindrome("abba")       == True
    assert is_palindrome("abcba")      == True
    assert is_palindrome("Able was I ere I saw Elba") == True
    assert is_palindrome("A man, a plan, a canal -- Panama!") == True
    assert is_palindrome("Never odd or even.")         == True
    assert is_palindrome("Not a palindrome. :(")      == False

# ── Predicate ───────────────────────────────────────────────────────────────

def startswith_prefix(prefix: str) -> Predicate[str]:
    return lambda x: x.startswith(prefix)


def ends_with_suffix(suffix: str) -> Predicate[str]:
    return lambda x: x.endswith(suffix)


def match_one_of_predicates(pred1: Predicate[str], pred2: Predicate[str]) -> Predicate[str]:
    return lambda x: any(map(lambda p:p(x), [pred1, pred2]))



def starts_and_ends_with_prefixes(
        prefix1: str,
        prefix2: str
    ) -> Predicate[str]:
    return lambda x: x.startswith(prefix1) and x.startswith(prefix2)


def starts_or_ends_with_prefixes(
        prefix1: str,
        prefix2: str
    ) -> Predicate[str]:
    return lambda x: x.startswith(prefix1) or x.startswith(prefix2)



def starts_or_ends_with_any_prefixes(pxs: tuple[str, ...]) -> Predicate[str]:
    return lambda x: any(map(lambda px:x.startswith(px), pxs))




def is_even(n: int) -> bool:
    return n % 2 == 0

def is_odd(n: int) -> bool:
    return not is_even(n)

def is_positive(n: int) -> bool:
    return n > 0

def is_negative(n: int) -> bool:
    return not is_positive(n)

def is_nonnegative(n: int) -> bool:
    return is_positive(n) or n == 0

def is_nonpositive(n: int) -> bool:
    return is_negative(n) or n == 0


def is_multiple_of_7(n: int) -> bool:
    return n % 7 == 0

def is_multiple_of_9(n: int) -> bool:
    return n %