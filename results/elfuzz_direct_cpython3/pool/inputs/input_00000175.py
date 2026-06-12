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
import inspect
import marshal
import os
import pickle
import pprint
import random
import re
import struct
import sys
import types
import typing
import weakref
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from functools import partial
from itertools import count, cycle, repeat
from operator import add, mul
from pathlib import Path
from types import CodeType

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence
    from typing import Any, Literal, Optional, TypedDict

PathLike = typing.Union[typing.IO, Path, str]

# ── Disassembly ──────────────────────────────────────────────────────────────


def disassemble(codeobj: CodeType) -> None:
    print(f"--{codeobj.co_name}--")
    dis.dis(codeobj)

# ── Global variables ──────────────────────────────────────────────────────────


sys.path.insert(0, ".")

GLOB_VAR = 123

# ── Module functions ──────────────────────────────────────────────────────────


def show_module(module: importlib.MimicModule):
    """Show some module's contents."""
    print(f"module: {module}")
    print("modules:", dir(sys.modules))
    print("sys.modules:", pprint.pformat(sys.modules))

# ── Functions as values ────────────────────────────────────────────────────────


# ── Lambda example ────────────────────────────────────────────────────────────


def lambda_example():
    max_5 = lambda l: sorted(l)[-5:]
    print(max_5([9, 7, 5, 4, 2]))
    print(max_5(range(5)))

# ── Partial application example ────────────────────────────────────────────────


def partial_application_example(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """
    >>> def sum(a, b, c):
    ...     return a + b + c
    ...
    >>> fp = partial(sum, 10)
    >>> fp(5, 6)
    21
    >>> fp(42)
    52
    >>> fp(3, 4, c=100)
    143
    """

    @functools.wraps(func)
    def wrapped(*a, **kw):
        return
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


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

