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
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NoReturn,
    Optional,
    Tuple,
    Union,
    overload,
    TYPE_CHECKING,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    get_type_hints_from_call,
    Literal,
    TypeVar,
    TypeGuard,
    Protocol,
    runtime_checkable,
    TypeAlias,
)
import sys
import types
import weakref

if TYPE_CHECKING:
    from collections.abc import Sequence
    S = TypeVar("S", bound=Sequence[Any])
else:
    S = TypeVar("S", bound="Sequence[Any]")


# ── Assertions ───────────────────────────────────────────────────────────────

assert isinstance(b"a", bytes)
assert isinstance(a := b"a".decode(), str)
assert any([a])

for i in range(3): assert a + b"\x00\x01"

try:
    assert a + "\x00\x01"
except TypeError:
    pass

try:
    assert a + ("\x00\x01",)
except TypeError:
    pass

try:
    assert a + [b"\x00\x01"]
except TypeError:
    pass

try:
    assert a + [[b"\x00\x01"]]
except TypeError:
    pass

try:
    assert a + {"one": b"\x00\x01"}
except TypeError:
    pass

try:
    assert a + ((1,),)
except TypeError:
    pass

try:
    assert a + {(1): b"\x00\x01"}
except TypeError:
    pass

print(len(list(range(4))), len(tuple(range(4))))

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + {}
except TypeError:
    pass

try:
    assert a + []
except TypeError:
    pass

try:
    assert a + dict(one=b"\x00\x01")
except TypeError:
    pass

print(a)

try:
    assert a + b""
except TypeError:
    pass

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + ""
except TypeError:
    pass

print(a * 2)

try:
    assert a * (-2,)
except TypeError:
    pass

try:
    assert a * (-2)
except TypeError:
    pass

try:
    assert a * ("")
except TypeError:
    pass

try:
    assert a * (None,)
except TypeError:
    pass

print(a * (a,))

try:
    assert a * (a,)
except TypeError:
    pass

try:
    assert a * (a, a)
except TypeError:
    pass

try:
    assert a * (a, a,)
except TypeError:
    pass

try:
    assert a * (a, a, a)
except TypeError:
    pass

try:
    assert a * (a, a, a,)
except TypeError:
    pass

try:
    assert a * (a, a, a, a)
except TypeError:
    pass

try:
    assert a * (a, a, a, a,)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a,)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a, a)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a, a,)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a, a, a)
except TypeError:
    pass

try:
    assert a * (a, a, a, a, a, a, a,)
except TypeError:
    pass

del aimport itertools
import os
import pickle
import platform
import pprint
import re
import signal
import socket
import sys
import time
import types
import tracemalloc
import typing as t
import uuid
import _thread as thread

if hasattr(thread, "_local"):
    from threading import Lock as ThreadLocalLock
else:
    class ThreadLocalLock(object):
        def __init__(self):
            self.lock = threading.Lock()
            self.release_count = 0

        def acquire(self, blocking=True, timeout=None):
            if self.release_count == 0:
                self.lock.acquire(blocking, timeout)
            else:
                self.release_count += 1

        def release(self):
            self.release_count -= 1
            if self.release_count <= 0:
                self.lock.release()

        def locked(self):
            return self.locked_locked or self.release_count < 0

        def set_lock(self, lock):
            self.lock = lock

        def __enter__(self):
            self.acquire()

        def __exit__(self, exc_type, exc_value, traceback):
            self.release()


class UUID(t.TypedDict):
    """A UUID object."""

    data: bytes


# ── Python internals ──────────────────────────────────────────────────────────

def get_current_frame(depth: int = 1) -> types.FrameType | None:
    """
    Return the current frame.

    The depth parameter specifies how many frames above the current one to go.
    For example, depth=1 will return the frame that called this function.
    """
    try:
        return sys._getframe(depth).f_back    # type: ignore[attr-defined]
    except ValueError:
        print(f"No frame at {depth} levels up.")
        return None


def frame_info_func(func: types.FunctionType) -> tuple[str, ...]:
    """Return the arguments and the locals dictionary associated with func."""
    args, _, _, defaults = inspect.getargspec(func)
    sig_str = ", ".join(args[-len(defaults):])    # omit positional default values
    sig = f"{func.__module__}.{func.__name__}({sig_str})"
    locals_ = inspect.currentframe().f_locals.copy()
    del locals_[func.__code__.co_varnames[0]]      # remove 'self' argument
    return (sig,) + tuple(locals_.values())


def stacktrace(limit: int =    while frame is not None:
        names.append(frame.f_code.co_name)
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
