"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))
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


def add_with_kwargs(
        *args: Union[int, str], a: int = 1, b: int = 2, c: int = 3
) -> None:
    print(f"a={a}, b={b}, c={c}")


def call_stack() -> int:
    for i in range(20):
        call_stack()
    else:
        return 0


def depth_probe(calls: int) -> None:
    if calls > 10000:
        raise RuntimeError()


def caller_info(level: int = 0) -> Callable[[Callable], Callable]:
    """
    >>> @caller_info(0)
    ... def f():
    ...     pass

    >>> f.__name__
    <function caller_info.<locals>.f at 0x7fb98d83e680>
    >>> f.__code__.co_filename.split('/')[-1] == __file__
    True
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            frame = sys._getframe(level + 1)
            name = frame.f_code.co_name or "<lambda>"
            filename = frame.f_code.co_filename.split('/')[-1]
            lineno = frame.f_lineno
            globals_ = frame.f_globals
            locals_ = frame.f_locals
            return func(*args, **kwargs)

        wrapper.__name__ = name
        wrapper.__code__ = getattr(wrapper, "__wrapped__").__code__
        wrapper.__globals__ = globals_
        wrapper.__dict__ = {}
        wrapper.__traceback__ = None
        wrapper.__closure__ = getattr(wrapper, "__wrapped__").__closure__

        return wrapper

    return decorator


def inject_local(
    local_vars: dict[str, object],
    *args: Any,
    **kwds: Any,
) -> tuple[Any, ...]:
    """
    Injects the given dictionary of variables into each argument.

    >>> inject_local({'x': 2})([1])
    (3,)
    """

    args = list(args)
    for idx, arg in enumerate(args):
        if not isinstance(arg, tuple):
            continue
        if len(arg) != len(local_vars.keys()):
            continue
        kwargs = {k: v for k, v in zip(local_vars.keys(), arg)}
        args[idx] = local_vars.values()

    return (*args, **kw