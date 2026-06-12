"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Set
from dataclasses import dataclass, field
from functools import partial
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from itertools import chain, cycle, dropwhile, groupby, tee
from math import ceil, log2
from pathlib import Path
from random import shuffle
from time import monotonic as timer
from threading import Thread
from typing import (
    Callable, ClassVar, Coroutine, TypeAlias, TypeGuard, TypedDict, Unpack, cast,
    overload
)

import array
import enum
import json
import logging
import os.path
import queue
import re
import signal
import sys
import tempfile
import time
import traceback
import warnings
import zlib

import anyio
import anyio.to_thread
import asyncio
import ctypes
import ipaddress
import multiprocessing.pool
import queue
import selectors
import ssl
import threading
import types
import typing
import urllib.request

if typing.TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator, Mapping, MutableMapping, Sequence
else:
    class Generator: pass
    class Iterable: pass
    class Iterator: pass
    class Mapping: pass
    class MutableMapping: pass
    class Sequence: pass

# ── Logging helpers ────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── AsyncGenerator tests ───────────────────────────────────────────────────────

@overload
async def test_async_gen(a: int) -> int: ...

@overload
async def test_async_gen(b: float) -> float: ...

async def test_async_gen(c: complex) -> complex:
    print(f"test_async_gen({repr(c)})")
    await asyncio.sleep(.5)
    yield c.real
    yield c.imag
    logger.debug("Done!")


# ── Logging ───────────────────────────────────────────────────────────────────

def log_error(msg: str):
    try:
        raise ValueError(msg)
    except ValueError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        lines[-1:] += ["  ..."]
        logger.error(f"{exc_value}\n{''.join(lines)}")

try:
    _log_exceptions = True
except NameError:
    _log_exceptions = False

if _log_exceptions:

    @contextlib.contextmanager
    def log_on_except():
        try:
            yield
        except BaseException as exc:
            if isinstance(exc, StopIteration):
                logger.warning(
                    "%r iteration stopped unexpectedly; no reason specified",
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
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
    header = struct.pack(HEADER_FMT, magic, version_major, version_minor, tag)
    return header + b"\x00" * (HEADER_SIZE - len(header))  # padding to align with 8-byte boundary


def unpack_header(buf: memoryview) -> tuple[int, int, bytes]:
    return struct.unpack(HEADER_FMT, buf[:HEADER_SIZE])


# ── Array packing ─────────────────────────────────────────────────────────────

def int_array(size: int, value: int) -> array.array:
    """Create an integer array with given size and content."""
    arr = array.array("i")             # signed 32-bit integers
    arr.extend([value] * size)
    return arr


def str_array(size: int, value: str) -> array.array:
    """Create a string array with given size and content."""
    arr = array.array('c', value.encode())
