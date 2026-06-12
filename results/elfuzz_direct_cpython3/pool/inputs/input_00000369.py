"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          traceback
"""

import os
import sys
from typing import Any, Callable, Dict, List, Tuple, Union

import ctypes
import functools
import itertools
import math
import operator
import random
import string
import subprocess
import threading
import timeit
import types
import typing
import unittest
import warnings
import weakref
import zlib
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from typing import MutableMapping, Sequence, Set, TypeVar, cast

import array
import enum
import gc
import gzip
import inspect
import marshal
import multiprocessing as mp
import platform
import queue
import re
import signal
import socket
import sqlite3
import ssl
import stat
import struct
import tempfile
import threading
import time
import traceback
import uuid
import urllib.parse
import urllib.request
import zipfile
import zlib

from contextlib import closing
from dataclasses import dataclass
from distutils.version import StrictVersion
from fractions import Fraction
from numbers import Rational
from pprint import pp, pformat
from statistics import mean
from timeit import Timer
from typing import ClassVar, Literal, TypedDict

try:
    from importlib.metadata import entry_points
except ImportError:                       # No module named 'importlib.metadata'
    from importlib_metadata import entry_points


__all__ = (
    "add",
    "add_no_op",
    "add_with_kwargs",
    "call_stack",
    "depth_probe",
    "caller_info",
    "inject_local",
    "pack_header",
    "unpack_header",
    "interleave_struct",
    "array_ops",
    "countdown_timer",
    "profile_decorator",
    "timeit_demo",
    "test_timeit_calls",
)

DEFAULT_LIB_PATHS = [
    "/usr/local/lib/python{}/site-packages".format(sys.version_info[0]),
]

T = TypeVar("T")
U = TypeVar("U")

# ── Common utilities ──────────────────────────────────────────────────────────


def add(a: T, b: U) -> tuple[T, U]:
    return a, b


@functools.lru_cache(maxsize=512)
def add_no_op(a: int, b: int) -> int:
    return a + b


@functools.lru_cache(maxsize=None)
def add_with_kwargs(*args, **kwargs) -> int:
    return sum(args) +    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(n: int = -1) -> str:
    """Return the name of the nth calling function (default to top level)."""
    n += 1
    if n >= len(depth_probe()):
        raise IndexError(f"{n} exceeds maximum recursion depth ({len(depth_probe())})")
    _, fnname, _, _, _ = inspect.getinnerframes(sys._getframe())[n]
    return fnname


def inject_local(name: str = "__local", value: Any = None):
    """
    Inject a local variable into all frames in this process.

    Useful for testing (e.g. `pytest --pdb`).
    """
    frame = sys._getframe()

    def iter_frames():
        yield frame
        try:
            while True:
                frame = frame.f_back
                yield frame
        except RecursionError:
            pass

    with warnings.catch_warnings():             # Avoid warning about unbound variables.
        warnings.filterwarnings(action="ignore", message=r"^'global'")
        for f in iter_frames():
            globals_ = f.f_globals.copy()
            del globals_[name]                   # Don't pollute global namespace.
            f.f_globals.update(globals_)
            locals_ = f.f_locals.copy()
            locals_.update({"name": value})
            f.f_locals.clear()
            f.f_locals.update(locals_)


def get_frame_lineno(fn: Callable[..., Any]) -> int:
    """Determine the line number where the given function was defined."""
    frame = sys._getframe().f_back
    filename = inspect.getsourcefile(inspect.unwrap(fn))
    lineno = next(line for line in reversed(inspect.getsourcelines(fn)[1])
                  if line == filename)
    return lineno


def get_caller_filename_and_line_number(
        n: int = -1) -> Tuple[Union[None, str], Union[int, None]]:
    """Get the file name and line number of the nth call above this point."""
    n += 1
    if n > len(depth_probe()):
        return None, None
    lines: list[str] = []
    frame = sys._getframe(n)
    while lines[-1] != "<module>":
        lines.append(cast(str, frame.f_code.co_filename))
        frame = frame.f_back
    return "\n".join(lines[-1:-1-n-1:-1]), lines[-1-n]


def test_get_caller_filename_and_line_number() -> None:
    def

# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
