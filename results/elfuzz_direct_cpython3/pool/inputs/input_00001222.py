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
    TypeGuard,
    TypeVar,
    Union,
)
from types import TracebackType
from typing_extensions import Concatenate, get_args, get_origin, get_type_hints, never_type_check

# TODO: add more test cases for the above modules and functions


def main() -> None:
    """Main function."""
    # noinspection PyTypeChecker
    print("Hello, world!", end="")
    print("Goodbye, world!")

    a = "a"
    b = 123_345.987_654_321e-987_654
    c = True
    d = 1 + 2j
    e = [a, b]
    f = {"key": b}
    g = {c: d}
    h = {f"Key_{i}": i ** 2 * 0xff for i in range(10)}
    assert len(h) == 10
    i = frozenset(e)

    j = (a,)
    k = ("a",)
    l = (*k,)
    m = [*l]
    n = ["a"]
    o = ["b"]
    p = [*o, *n]
    q = []
    r = [*q, *p]

    s = e[0]
    t = e[-1]
    u = e[:1]
    v = e[:-1]
    w = e[1:-1]

    x = e[::1]
    y = e[::-1]
    z = e[::-1][::-1]

    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r = range(20)

    assert isinstance(a, int)
    assert isinstance(b, str)
    assert isinstance(c, bool)
    assert isinstance(d, complex)
    assert isinstance(e, list[Any])
    assert isinstance(f, dict[str, float])
    assert isinstance(g, dict[bool, complex])
    assert isinstance(h, dict[str, int])
    assert isinstance(i, frozenset[str])
    assert isinstance(j, tuple[int])
    assert isinstance(k, tuple[str])
    assert isinstance(l, tuple[tuple[str]])
    assert isinstance(m, tuple[list[int]])
    assert isinstance(n, tuple[list[str]])
    assert isinstance(o