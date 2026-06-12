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


class A:
    pass


class B(A):
    pass


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
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

