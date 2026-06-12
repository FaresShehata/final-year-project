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
    # working with strings. We've already used one of them, `tokenize`, in the
    # previous exercise. There are other ways to parse strings into lists of
    # tokens though!

    # First up is `ast.literal_eval`. This function takes a string as input and
    # returns an arbitrary python construct from that string. For instance, if
    # you pass it `"1 + 2i * 3j / 4 - 5"` it will return `1+2j*3/4-5`.

    assert ast.literal_eval("1 + 2i * 3j / 4 - 5") == 1 + 2j * 3 / 4 - 5
    assert ast.literal_eval("{1 + 2i}") == {1 + 2j}
    assert ast.literal_eval("[1, 'a', True, ...]") == [
        1,
        "a",
        True,
        ...
    ]
    assert ast.literal_eval('{"a": 1}') == {"a": 1}

    # Another way to do this is to use `textwrap.dedent`. This removes leading
    # whitespace from each line in the string. So for example, if I have a file
    # like this:

    with open("test.txt", mode="w") as f:
        f.write("""\
a = 1
""")


    # Then calling `textwrap.dedent(test.txt)` on it yields:

    assert textwrap.dedent(open("test.txt").read()) == """\
a = 1"""


    # The reason we were using this string as an argument was because we wanted
    # to show how much whitespace gets removed when we call `tokenize.tokenize`.
    # If we didn't want to see the extra newlines between lines, then we could
    # just pass the string directly to `tokenize.tokenize`. Here's what happens
    # when we do that:

    source_lines = list(tokenize.tokenize(ast.parse(textwrap.dedent(open("test.txt").read())).co_code))
    source = "".join(source_line[1][0].strip() for source_line in source_lines)

    assert source.startswith("a")
    assert source.endswith("=")

    # One more thing you might notice here is the use of `ast.parse`. You can
    # think of this as Python's version of the command-line interpreter; it runs
    # your code and gives you back output. It does this by parsing your code