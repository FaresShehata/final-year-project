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

# ── TypeAlias ──────────────────────────────────────────────────────────────── #

StrList: TypeAlias = list[str]
IntTuple: TypeAlias = tuple[int, ...]

# ── ClassVars ─────────────────────────────────────────────────────────────── #

SOME_STR: Final[str] = "some str"
MULTI_LINE_STR = """this is a \n multi-line string"""
THIS_IS_A_MULTI_LINE_STRING = MULTI_LINE_STR
SEPARATE_MULTI_LINE_STR = """
This is the first line of a multi-line string.
The second line starts here.
"""
REPEATED_SINGLE_QUOTE: Final[str] = "'"

# ── Enumerators ───────────────────────────────────────────────────────────── #

class Colors(str, enum.Enum):
    RED:   Final[str] = "\u001b[31m"
    GREEN: Final[str] = "\u001b[32m"
    RESET: Final[str] = "\u001b[0m"

def print_red(text: str) -> None:
    print(Colors.RED + text + Colors.RESET)
    
print_red(SOME_STR)

# ── TypedDict ─────────────────────────────────────────────────────────────── #


MyDict: TypedDict = {"a": int}
x: MyDict = {"a": 1}
y: MyDict = {"a": float}

# ── Annotated ─────────────────────────────────────────────────────────────── #


MyAnnotatedClass: type = Annotated["SomeClass", "docstring"]


def foo(x: MyAnnotatedClass) -> None:
    pass

foo(MyAnnotatedClass())

x: Annotated[type, "docstring"] | None = None # T is not annotated
y: Annotated[int, "docstring"] | None = None # T is an instance of type
z: Annotated[int, "docstring"] | str = 1 # T is an instance of int or str
zz: Annotated[int, "docstring"] | str = "hello world!" # T is an instance of int or str

for i in range(3):
    x: Annotated[int, f"docstring{i}"] | None = None


def bar(*args: Annotated[Any, "docstring"], **kwargs: Annotated[Any, "docstring"]) -> None:
    pass

bar(a=1, b="hello")


# ── ParamSpec ───────────────────────────────────────────────────────────────