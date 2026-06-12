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

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"
        self.type_ = getattr(owner, "__annotations__", {}).get(self.pub)

    def __set__(self, obj, val):
        if isinstance(val, self.type_):
            setattr(obj, self.priv, val)
        else:
            raise TypeError(f"{obj!r}.{self.pub} must be {self.type_}")


class PositiveInteger(_Constrained):
    type_ = int


class NonEmptyString(_Constrained):
    type_ = str


@dataclasses.dataclass(slots=True)
class HexBytes:
    """Wrapper around `bytes` with `.hex()` method and property accessors.

    >>> h = HexBytes.from_hex("ff00aabb")
    >>> h.hex()
    'ff00aabb'
    >>> h.bytes
    bytearray(b'\xff\x00\xaa\xbb')
    """

    data: bytes

    @classmethod
    def from_bytes(cls, bytes_) -> HexBytes:
        return cls(bytes_)

    @property
    def bytes(self) -> bytes:
        return self.data

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return f"<HexBytes {len(self.data):,}>"

    def hex(self) -> str:
        return self.data.hex()


# ── no-stdlib-namespace imports ────────────────────────────────────────────────

from collections.abc import Mapping, MutableMapping, Iterable, Callable
from contextlib import ContextManager, AbstractContextManager, suppress
from enum import Enum
from functools import partial, wraps, lru_cache
from operator import attrgetter, itemgetter, methodcaller
from importlib.util import find_spec, module_from_spec, spec_from_loader
from inspect import Parameter, Signature, signature
from itertools import chain, zip_longest, tee, count, product, islice, combinations_with_replacement
from logging import getLogger
from math import log, prod
from mmap import ACCESS_READ, mmap
from pyrsistent import PClass, field
from re import Pattern, compile, subn
from signal import SIGTERM, Signals
from socket import AF_INET, SOCK_STREAM, socket, setdefaulttimeout
from statistics import mean
from threading import Thread, RLock, Event, Timer
from traceback import format_exc
from typing import TYPE_CHECKING, cast
from warnings import warn
if TYPE_CHECKING:  # tests won't have the other modules installed
    from
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

