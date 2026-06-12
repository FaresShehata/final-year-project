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
import os
import re
import shutil
import subprocess
import sys
import tokenize
from asyncio.base_events import BaseEventLoop
from collections.abc import Callable, Iterator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor as ThreadingPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from functools import partial, wraps
from inspect import Parameter, signature
from itertools import chain, repeat
from multiprocessing.pool import Pool
from pathlib import Path
from pprint import pformat
from random import randint
from re import match
from secrets import token_bytes
from signal import SIGINT, signal
from statistics import mean, median, stdev
from threading import Thread
from time import sleep
from types import ModuleType, FunctionType
from typing import (
    Any, AsyncGenerator, Awaitable, Literal, TypeVar, Protocol, runtime_checkable,
)
from typing_extensions import Self, ParamSpec, ClassVar, NotRequired, TypedDict, \
                               TypeGuard, Unpack, Final, TypeAlias, Annotated, \
                               never_typecheck, unpack_var, finalize, final, \ 
                               get_args, get_origin, get_origin, get_origin, \
                               get_args, get_origin, get_args, get_origin, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
                               get_origin, get_args, get_origin, get_args, \
    def __init__(self, maxval: int):
        super().__init__()
        self.max = maxval

    def __call__(self, value: int) -> int:
        return min(value, self.max)


def minmax(minval: int, maxval: int) -> tuple[int, int]:
    class MinMaxConstraint:
        def __call__(self, value: int) -> int:
            return max(minval, min(maxval, value))
    return MinMaxConstraint(), MinMaxConstraint()


class NonEmptyString(str):
    def __new__(cls, value: str):
        if value == "":
            raise ValueError("Non-empty strings must be provided!")
        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f'"{super().__str__()}"'


def lower_case(s: str) -> str:
    return s.lower()


def upper_case(s: str) -> str:
    return s.upper()


def capitalize(s: str) -> str:
    return s.capitalize()


def title_case(s: str) -> str:
    return s.title()


def swap_case(s: str) -> str:
    return s.swapcase()


def reverse_string(s: str) -> str:
    return s[::-1]


def split_string(s: str, sep: str | None = None) -> list[str]:
    return s.split(sep)


def join_strings(lst: list[str], sep: str) -> str:
    return sep.join(lst)


def replace_char(s: str, old: str, new: str) -> str:
    return s.replace(old, new)


def count_occurrences(s: str, char: str) -> int:
    return s.count(char)


def find_index(s: str, char: str) -> int:
    return s.find(char)


def find_last_index(s: str, char: str) -> int:
    return s.rfind(char)


def remove_characters(s: str, chars: str) -> str:
    return s.translate(str.maketrans("", "", chars))


def strip_spaces(s: str) -> str:
    return s.strip()


def lstrip_spaces(s: str) -> str:
    return s.lstrip()


def rstrip_spaces(s: str) -> str:
    return s.rstrip()


def pad_string(s: str, width: int, fillchar: str = " ") -> str:
    return s.center(width, fillchar)


def truncate_string(s: str, length: int, end: str | None = "...") -> str:
    return s[:length] + end if length < len(s) else s


def truncate_and_add_chars(s: str, length: int, chars: str | None = None) -> str:
    return s[:length].ljust(length, chars) if chars else s[:length]


def align_string(s: str, alignment: Literal["left", "right", "center"], width: int) -> str:
    if alignment == "left":
        return s.ljust(width)
    elif alignment == "right":
        return s.rjust(width)
    elif alignment == "center":
        return s.center(widthADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c

assert add3(1)(2)(3) == 6
assert add3(4, 5, 6) == 15


@curry
def mul3(a: int, b: int, c: int) -> int:
    return a * b * c


assert mul3(1)(2)(3) == 6
assert mul3(4, 5, 6) == 120


# ── Partial application with arguments passed as keyword-only parameters ────────

def curry_partial(func: Callable, /, *, args=None, kwargs=None) -> Callable:
    """Curries the given function with partially applied positional or keyword
    arguments.
    """
    if args is None:
        args = tuple()

    if kwargs is None:
        kwargs = {}

    @functools.wraps(func)
    def decorated_func(*positional_args: A, **keyword_args: B) -> Callable:
        all_args = (*args, *positional_args)
        all_kwargs = {**kwargs, **keyword_args}
        return func(*all_args, **all_kwargs)

    return decorated_func


add3_1: Callable[[A], Callable[[B], Callable[[C], A]]] = curry_partial(add3)
mul3_1: Callable[[A], Callable[[B], Callable[[C], A]]] = curry_partial(mul3)


assert add3_1(1)(2)(3) == 6
assert mul3_1(1)(2)(3) == 6


# ── Trampoline (finalizer) pattern ────────────────────────────────────────────

def trampoline(fn: Callable[..., T]) -> Callable[..., T]:
    """Trampoline pattern.

    Wraps a potentially recursive function so that it can be called repeatedly
    until it returns a non-recursive value.

    Args:
      fn: Function to wrap.

    Returns:
      Wrapped function which calls fn recursively.

    Example:

      >>> @trampoline
      ... def factorial(n: int) -> int:
      ...     if n <= 1:
      ...         return 1
      ...     else:
      ...         return n * factorial(n - 1)

      >>> factorial(8)
      40320
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwds):
        while True:
            res = fn(*args, **import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
