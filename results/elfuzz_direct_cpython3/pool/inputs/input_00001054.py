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
import timeit
import types
import typing
import typing_extensions as te
import urllib.parse
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import (
    MutableMapping,
    Sequence,
)
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from itertools import chain, cycle, tee
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import sample
from re import Pattern
from sys import argv
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    NewType,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID
from zlib import crc32
from warnings import warn


class A:
    def b(self):
        return "b"


def f() -> None:
    pass


# noinspection PyUnusedLocal
def g(x: int = 1):
    """docstring"""


def h(*args, **kwargs) -> None:
    pass


def i(a: str, /, b: int, c: float, d: bool, *, e: str, f: int) -> None:
    pass


def j(
    a: str,
    b: int,
    c: float,
    d: bool,
    *args: int,
    e: str,
    f: int,
    g: str,
    **kwargs: str,
) -> None:
    pass


def k(
    x: str,
    y: int,
    z: float,
    w: bool,
    *args: complex,
    **kwargs: complex,
) -> None:
    pass


def l(x: str, y: int = 10, /, z: float = 3.141592653589793, w: bool = True) -> None:
    pass


def m(*a, **kw) -> None:
    pass


def n(
    x: int,
    y: int,
    z: int,
    w: int,
    *a: int,
    u: int,
    v: int,
    w: int,
    **kw: int,
) -> None:
    pass


def o(
    x: int,
    y: int,
    z: int,
    w: int,
    *a: int,
    u: int,
    v: int,
    w: int,
    **kw: int,
    t: int,
) -> None:
    pass


def p(x: str) -> None:
    print(x)


def q(y: str | int) -> None:
    if isinstance(y, str):
        print(y)
    elif isinstance(y, int):
        print("int", y)
    else:
        raise TypeError(f"y must be str or int but is {type(y)}")


def r(x: str | int) -> str:
    if isinstance(x, str):
        return x.upper()
    elif isinstance(x, int):
        return str(x).upper()
    else:
        raise TypeError(f"x must be str or int but is {type(x)}")


def s(x: str | int | float) -> str | int | float:
    if isinstance(x, str):
        return x.upper()
    elif isinstance(x, int):
        return str(x).upper()
    elif isinstance(x, float):
        return round(float(x), 2)
    else:
        raise TypeError(f"x must be str or int or float but is {type(x)}")


def t(x: str | bytes) -> bytes:
    try:
        return x.encode("utf-8")
    except AttributeError:
        raise TypeError(f"{x} must be str or bytes but is {type(x)}")


def u(x: str | bytes) -> str:
    try:
        return x.decode("utf-8")
    except AttributeError:
        raise TypeError(f"{x} must be str or