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
    NewType,
    NamedTuple,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from types import FunctionType
from weakref import WeakValueDictionary
import sys


def _oob():
    return "Out of bounds"


assert len("a") == 1, _oob()


class A:
    def foo(self):
        pass


A().foo()
B = type("B", (), {})

print(B.__module__)
print(B.__name__)


# https://github.com/python/cpython/blob/3.9/Lib/tokenize.py
tokens = [
    # http://docs.python.org/reference/lexical_analysis.html#literals
    'r"abc"', '"def"',
    r'b"abc"', "'def'",  # Invalid: b"" is not a literal.
    r"'\\n'", r'"\\n"', r'r"\\"', r'b"\\""',
    r'\x27\x22\t\n\v\f\r\b\a\u1234\U1234',
    r'\N{GREEK SMALL LETTER DELTA}',
    '\uFFFF',
    "\uFFFF",
    '\U0010ffff',
    "\U0010ffff",
    '\x80-\xff',
    '\u10000-\uffff',
    "\u10000-\uffff",
    '\U00101000-\U0010ffff',
    "\U00101000-\U0010ffff",
]

for t in tokens:
    print(t)


class C:
    ...


C()
D = type("D", (object,), {})()

try:
    D()
except TypeError as e:
    # SyntaxError
    # NameError: name 'c' is not defined
    assert str(e).startswith("type object 'D' has no attribute '__call__'")
else:
    raise AssertionError(_oob())


class E:
    pass


E()
F = type("F", (object,), {"__call__": lambda self: None})()

try:
    F()
except TypeError as e:
    # SyntaxError
    # NameError: name 'f' is not defined
    assert str(e) == "__call__() missing 1 required positional argument: 'self'"
else:
    raise AssertionError(_oob