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
import shutil
import sys
import tokens
from ast import literal_eval, parse
from collections import deque
from concurrent.futures import Future
from functools import wraps
from heapq import merge
from itertools import chain, combinations, count, cycle, groupby, permutations, repeat
from inspect import Parameter, signature
from io import StringIO
from operator import le, lt, ne
from pathlib import Path
from random import randint, seed
from re import M, finditer, match
from signal import SIGINT
from statistics import mean
from string import Formatter as SF
from string import Template as ST
from subprocess import PIPE, Popen, run
from time import sleep
from types import FunctionType, ModuleType, TracebackType
from typing import (
    Any, Callable, ClassVar, Deque, Dict, Generic, Iterator, List, Literal, Match,
    NamedTuple, Optional, Pattern, Set, Tuple, Type, Union, cast, overload
)
from typing_extensions import Annotated, Concatenate, Final, Never, ParamSpec, Self, TypeAlias, TypeGuard, TypedDict, get_args
from unittest.mock import Mock
from urllib.parse import urlencode
from weakref import WeakSet

from _testcases.helpers import (
    assert_eq, assert_ne, debug_print, display, display_caller_frame, display_stack_trace, display_var, expect_success,
    is_implementation_error, is_syntax_error, raise_ex, test, xfail, yield_from_ex_generator, yield_from_ex_coroutine
)
from _utils import (
    debug_print, display, display_caller_frame, display_stack_trace, file_lines_iter, print, script_dir, temp_file_path
)



# ── Builtin functions ─────────────────────────────────────────────────────────

def abs_(x: int) -> int:
    return max(-x, x)

def all(iterable: Iterable) -> bool:
    return not any(not x for x in iterable)

def any(iterable: Iterable) -> bool:
    for x in iterable:
        if x:
            return True
    return False

def ascii(obj: Any) -> str:
    return repr(obj).replace("'", '"')

def bin(i: int) -> str:
    return format(i, '#b')[2:]

def callable(obj: Any) -> bool:
    return isinstance(obj, (FunctionType, MethodType, classmethod, staticmethod))

def chr(i: int) -> str:
    return chr(i
TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
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


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
