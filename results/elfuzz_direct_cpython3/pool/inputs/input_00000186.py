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
from typing_extensions import ParamSpec, Concatenate, TypeAlias


def seed_05() -> None:

    # → 1. Threadsafe datastructures

    print("1. Threadsafe datastructures")

    # Python has two main thread-safe collections: `threading.Lock`-synchronized
    # dicts and `threading.RLock`-synchronized dicts (named after the lock they
    # use). *In this exercise*, we'll implement our own thread-safe dictionary.

    class ThreadSafeDict(dict):
        _lock: threading.Lock = threading.Lock()

        def __getitem__(self, key: object) -> object:
            with self._lock:
                return super().__getitem__(key)

        def __setitem__(self, key: object, value: object) -> None:
            with self._lock:
                super().__setitem__(key, value)

    a = ThreadSafeDict({"a": 1})
    b = ThreadSafeDict(
        {
            "b": {"c": [3, 2], "d": {"e": 4}},
            "f": 5,
        }
    )

    assert a["a"] == 1
    a["a"] = 42
    assert a["a"] == 42
    del a["a"]
    assert not ("a" in a)

    assert b["b"]["c"][1] == 2
    b["b"]["c"].append(99)
    assert b["b"]["c"][-1] == 99
    assert b["b"]["c"] == [3, 2, 99]

    assert repr(a) == "{...}"
    assert repr(b) == "{...}"

    # → 2. String parsing

    print("\n2. String parsing")

    # In this section, we're going to be learning about some libraries for
    # working with strings. We've already used one of them, `tokenize`, in
    # `seed_02`. Let's do a quick review of that library first.

    print(f"\n-> {tokenize.__doc__}")

    # Okay, so what can we do with it? Well, *we* need to learn how to read
    # tokens from a file or byte stream. That means, we need to know how to
    # parse a token stream into something useful. The best way to do that is
    # probably    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

