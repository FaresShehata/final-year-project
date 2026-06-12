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
import sys
import threading
import types
import typing
import uuid
import warnings
import weakref
import zlib
from collections.abc import AsyncGenerator, Generator, Sequence, Sized
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from functools import cache, lru_cache, wraps
from itertools import count, cycle, islice, tee, zip_longest
from operator import attrgetter, itemgetter
from platform import python_version_tuple
from re import Pattern, compile, finditer, subn
from signal import SIGINT, SIGTERM, Signals
from socket import AF_INET, SOCK_STREAM, SHUT_RDWR, error as SocketError
from subprocess import PIPE, Popen, TimeoutExpired, check_output
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from threading import Event, Lock, Thread
from textwrap import dedent
from time import perf_counter_ns, sleep
from types import TracebackType
from typing import TYPE_CHECKING, Any, NoReturn, Self, SupportsBytes, SupportsFloat
from urllib.request import urlopen
from zlib import compressobj, decompressobj

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
    from types import FrameType
else:
    def _typecheck(obj):
        if not isinstance(obj, type(obj)):
            raise TypeError(f"expected an instance of the given type")
        return obj


T = TypeVar("T")

P = ParamSpec("P")


class MyEnum(Enum):
    """An example class."""

    ONE = 1
    TWO = 2


class MyOtherEnum(MyEnum):
    """Another example class."""


class Data(TypedDict):
    key1: str
    key2: int
    key3: float


def insert_into_array(array: list[int], index: int, element: int) -> None:
    array.insert(index, element)


def process(arg1: str, arg2: int, arg3: float) -> tuple[str, int, float]:
    return f"{arg1} {arg2}", arg1[arg2 : arg2 + 1], arg3 // 2


def process_2(*args: str, **kwargs: int) -> tuple[tuple[str, ...], tuple[int, ...]]:
    return args, kwargs.values()


def process_with_defaults(
    *, kwarg1: str = "", kwarg2: int = 42, kwarg3: float = 3.14
) -> None:
    print(kwarg1, kwarg2, kwarg3)


def process_with_defaults(**kwargs) -> None:
    kwarg1, kwarg2, kwarg3 = kwargs["kwarg1"], kwargs["kwarg2"], kwargs["kwarg3"]
    print(kwarg1, kwarg2, kwarg3)


def process_with_defaults_kwonly(*, kwarg1: str = "") -> None:
    kwarg1, _, _ = kwarg1, *(), *
    print(kwarg1)


def process_with_defaults_posonly(arg1: str, /, arg2: int) -> None:
    _, arg2, _ = arg1[:], arg2, arg2 - 1
    print(arg1, arg2)


class A:
    pass


class B(A):
    pass<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>
class C(B):
    pass


def my_function(a: A | B | C) -> bool:
    """A function that accepts any one of its arguments' classes.

    Note that this uses the special `|` operator to specify multiple possible
    argument types.
    """
    return True


class MyClass:
    """Class with methods and attributes."""

    def method(self, arg1: str, arg2: int = 42) -> None:
        self.attr1 = arg1  # attribute
        self.attr2 = arg2  # attribute

    @classmethod
    def class_method(cls, arg1: str, arg2: int = 42) -> None:
        cls.class_attr1 = arg1  # class attribute
        cls.class_attr2 = arg2         names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
