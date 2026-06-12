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
Fruit:     TypeAlias = "Apple | Banana"

# ── TypedDict ─────────────────────────────────────────────────────────────────

UserRecord: TypedDict("UserRecord", {
    "id":     int,
    "created": int,
    "email":  str,
})

OrderRecord: TypedDict("OrderRecord", {
    "user_id":     int,
    "order_date":  int,
    "items_count": int,
})


# ─── Base Types ───────────────────────────────────────────────────────────────

class Employee(NamedTuple):
    id:       int
    salary:   float
    age:      int
    hire_date: int


class Fruit(NamedTuple):
    type_:     str
    color:     str
    shape:     str
    weight_g:  float


class User(NamedTuple):
    username:  str
    email:     str
    password:  str
    created_at: int


# ─── Fancier Nomenclature ─────────────────────────────────────────────────────-

class FooBar(BazQuux):
    ...


class Baz(Method):
    ...


# ─── String Manipulation ───────────────────────────────────────────────────────

def remove_comments(s: str) -> str:
    """
    Remove leading whitespace and comments from each line.

    >>> s = '''
    ... # comment
    ... def foo():  # another comment
    ...     print('hi')
    ...
    ... # last comment
    ... '''
    >>> remove_comments(s)
    'def foo():\n    print(\'hi\')'
    """

    buf = io.StringIO()

    for line in s.split("\n"):
        start = end = len(line)
        for idx, char in enumerate(line):
            if char == "#":
                end = idx - 1
                break
        buf.write(line[:start].rstrip())

    return buf.getvalue()


def normalize_line_endings(s: str) -> str:
    """
    Replace Windows (\r\n) and Mac (\r) newline terminators with Unix (\n).

    >>> normalize_line_endings('\r\nabc\rdef\rghi\rjkl\r\nmno\rpqr\rstu\r\nvwxyz')
    '\\nabc\\ndefghi\\njkl\\nmnopqrstuvwxyzz'

    Note that this does not handle mixed endings, only consecutive ones.
    """

    buf = io.StringIO()
   
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


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
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
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


# ── struct — binary unpacking ──────────────────────────────────────────────────

def unpack_user_record(raw: bytes) -> UserRecord:
    """Unpack user record data into a named tuple."""
    header_size = HEADER_SIZE
    offset      = header_size + 4  # skip timestamp (uint32)
    nfields     = struct.unpack(">H", raw[offset : offset + 2])[0]
    result      = [None] * nfields
    offset += 2

    for field_idx in range(nfields):
        fmt = ">B 4s"
        size = struct.calcsize(fmt)
