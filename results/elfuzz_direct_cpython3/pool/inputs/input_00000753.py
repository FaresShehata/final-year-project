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
from typing_extensions import Concatenate, get_args, get_origin, get_valuetypedefs_for_union


def foo(x: int | float):
    """Function foo."""
    ...


def bar():
    def baz():
        pass

    return baz()


def qux(*args: str, **kwargs: int):
    ...


def corge(foo: bool, bar: list[float], *baz: bytes, quux: dict[str, complex]) -> tuple:
    """
    Function `corge`.

    Args:
        foo (bool): A boolean value.
        bar (list[float]): A list of floats.
        baz (bytes): Bytes data.
        quux (dict[str, complex]): A dictionary with string keys and complex values.

    Returns:
        tuple: A tuple containing the sum of all elements in `bar` multiplied by `foo`, and the first element from `baz`.
    """
    # ...
    return 1.23, 4.56


def grault(key: str = "value") -> None:
    ...


def garply(*args: int, **kwargs: str) -> None:
    ...


def waldo() -> None:
    ...


def fred(a: int = 1, b: str = "", c: list[int] = [], d: dict[int, str] = {}):
    ...


def plugh(
    a: int = 1,
    b: str = "",
    c: list[int] = [],
    d: dict[int, str] = {},
    e: tuple[int, str] = (),
    f: set[int] = frozenset(),
    g: range(int) = range(10),
    h: bytes = b"hello",
    i: bytearray = bytearray(b"hello"),
    j: memoryview = memoryview("hello"),
    k: complex = 1 + 2j,
    l: float = 3.14,
    m: float = -987.654e-321,
    n: bool = True,
    o: bytes = b"",
    p: bytearray = bytearray(),
    q: memoryview = memoryview(""),
    r: complex = 9.87654e+321 + 12j,
    s: float = 123.456e-321,
