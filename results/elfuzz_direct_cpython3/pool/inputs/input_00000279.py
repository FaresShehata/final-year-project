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
import trace
import tracemalloc as tm
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial, reduce, singledispatchmethod
from itertools import accumulate
from operator import add
from pathlib import Path
from timeit import default_timer as timer
from typing import TYPE_CHECKING, Any, Literal, overload

if TYPE_CHECKING:
    from types import CodeType

    from _typeshed import SupportsReadBytes

# ─── PEP 570 Typed dictionary type aliases ───────────────────────────────────

_TypedDict = type({}) if sys.version_info >= (3, 9) else None

if _TypedDict is not None:

    @dataclass(frozen=True)
    class PyCodeAttributes(_TypedDict):
        """Python code object attributes."""

        co_argcount: int         # number of arguments including varargs and keywords
        co_posonlyargcount: int  # number of position-only arguments
        co_kwonlyargcount: int   # number of keyword only arguments
        co_nlocals: int          # number of local variables
        co_stacksize: int        # size of the stack required by this function
        co_flags: int            # flags influencing execution
        co_code: bytes           # byte string containing the bytecode produced by the compiler or interpreter
        co_consts: tuple         # constants used in the code
        co_names: tuple          # variable names used in the code
        co_varnames: tuple       # local variable names referenced in the code
        co_filename: str         # name of file defining code object
        co_name: str             # name given to function when defined
        co_firstlineno: int      # first line number to which the code belongs
        co_lnotab: bytes         # mapping between source lines and bytecode offsets
        co_freevars: tuple       # variable names that are cell objects
        co_cellvars: tuple       # variable names that refer to cell objects


@overload
def load_code_from_file(path: str | Path, mode: Literal["rb"]) -> CodeType:
    ...


@overload
def load_code_from_file(path: str | Path, mode: Literal["r"]) -> PyCodeAttributes:
    ...


def load_code_from_file(path: str | Path, mode: Literal["rb"] | Literal["r"]) -> CodeType | PyCodeAttributes:
    with    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


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

