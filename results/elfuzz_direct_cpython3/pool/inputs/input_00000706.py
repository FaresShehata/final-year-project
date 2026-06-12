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
U  = TypeVar("U", covariant=True)
V  = TypeVar("V")
K  = TypeVar("K")
S  = TypeVar("S", bound=type)
C  = TypeVar("C", bound=Callable[..., Any])
P  = ParamSpec("P")
F  = Any
R  = RE = Final[F]
X  = Xx = Final[Any]
N  = Nn = Final[int | None]
I  = Ii = Final[str | int | None]
D  = Dd = Final["Decimal"]
E  = EllipsisType = Final[...]
O  = Oo = Final[list[X]]
M  = Mm = Final[tuple[X]]
A  = Aa = Final[type[X]]
Q  = Qq = Final[str | list[str]]
W  = Ww = Final[io.TextIOBase]
H  = Hh = Final[pathlib.Path]
B  = Bb = Final[bytes | bytearray | memoryview]
L  = Ll = Final[float]
J  = Jj = Final[dict[str, T]]
Z  = Zz = Final[dict[str, dict[str, str]]]
Y  = Yy = Final[deque[Any]]
X  = Xx = Final[list[any]]
# TODO: fix type for l in [list]: https://github.com/python/typing/issues/789
L  = llll = Final[[Any]]

def _test() -> None:
    """Test solution."""
    # https://docs.python.org/3/library/decimal.html#module-decimal
    decimal = Decimal('1.2')
    print(decimal)
    # >>> 1.2
    print(type(decimal))
    # >>> <class 'decimal.Decimal'>
    print(dir(decimal))
    # >>> ['as_tuple', '__abs__', '__add__', ...]
    print(help(Decimal.as_tuple))
    # ...
    print(help(Decimal.add))
    # ...

    # https://docs.python.org/3/library/numbers.html
    number = 1
    if isinstance(number, numbers.Number):
        print(True)
    else:
        print(False)
    # True

    # https://docs.python.org/3/library/tokenize.html#tokenize.tokenize
    with open(__file__) as f:
        tokens = tokenize.generate_tokens(f.readline)
        for token in tokens:
            print(token)
    # TokenizeError: Unknown line continuation character '\'

    # https://docs.python.org/3/library/textwrap.html#textwrap.TextWrapper
    content = "This is a sample paragraph.\nIt contains multiple lines of text."
    wrapper = textwrap.TextWrapper(width=20)
    wrapped_content = wrapper.fill(content)
    print(wrapped_content)
    # This is a sample paragraph.
    # It contains multiple lines of text.

    # https://docs.python.org/3/library/string.html#string.Formatter.format
    name = "Alice"
    greeting = "{name}, welcome to Python!".format(name=name)
    print(greeting)
    # Alice, welcome to Python!

    #