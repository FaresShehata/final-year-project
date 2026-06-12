"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
import bisect
import collections.abc as col_abc
import enum
import functools
import importlib.metadata
import itertools
import json
import logging
import math
import numbers
import os
import pathlib
import pprint
import random
import re
import timeit
import typing as tp
import warnings
from datetime import timedelta
from multiprocessing import Pool
from pathlib import Path
from queue import Empty
from statistics import mean, median
from threading import Thread
from types import FunctionType, MethodType
from typing import (
    Any, Callable, Dict, Iterable, Iterator, List, Literal, Optional, Sequence, Set,
    Tuple, TypeVar, Union, cast, overload, runtime_checkable
)

import numpy as np
import pandas as pd
import requests
import semver
import threading
import types
import typing_inspect as ti
import urllib.parse
import weakref
import yaml

try:
    import cattrs
except ImportError:
    pass

if tp.TYPE_CHECKING:
    import tomlkit

__all__ = [
    "depth_probe",
    "caller_info",
    "inject_local",
    "pack_header",
    "unpack_header",
    "interleave_struct",
    "array_ops",
    "nuclear_threading",
    "make_adder_from_bytecode",
    "make_fn_from_bytecode",
]

T = TypeVar("T")
Func = tp.Callable[..., T]


class Bar(object):
    def __init__(self, bars: tp.Iterable[int]) -> None:
        self.bars = bars
        self.current_bar = iter(self.bars).next()

    def update(self) -> bool:
        if next(self.bars) == self.current_bar or self.bars.stop:
            return False
        print(f"\r{self.current_bar}", end="")
        self.current_bar = next(self.bars)
        return True

    @property
    def current_value(self) -> int:
        return self.current_bar - 1

    def total(self) -> int:
        return sum(self.bars)

    def percent_complete(self) -> float:
        return self.current_value / self.total()


@overload
def nuclear_threading(func: Func[T], nthreads: int) -> T:
    ...


@overload
def nuclear_threading(func: Callable[[int], T], args: int, nthreads: int) -> Iterator[T]:
    ...


def nuclear_threading(func: tp.Any,    new_fn = types.FunctionType(
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

