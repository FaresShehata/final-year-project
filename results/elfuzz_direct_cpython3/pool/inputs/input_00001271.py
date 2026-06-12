"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if objattr := getattr(obj, self.attrname, None):
            return objattr
        val = self.func(obj)
        setattr(obj, self.attrname, val)
        return val


# ── MetaClasses ───────────────────────────────────────────────────────────────

class BaseMeta(type):
    pass


class BaseClass(metaclass=BaseMeta):
    @classmethod
    def classmethod(cls):
        ...


@contextlib.contextmanager
def embedded_context_manager(*args, **kwargs):
    yield


class ContextManagerWrapper(BaseClass):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del(exc_type, exc_val, exc_tb)


class ClassWithMetaclass(BaseClass, metaclass=types.new_class("MyType", (BaseMeta,), {})):
    @classmethod
    def classmethod(cls):
        ...  # mypy doesn't like this -- it expects the function to be defined on the MainClass


# ── Generators ────────────────────────────────────────────────────────────────

def grouper(iterable, n: int, fill_value=None) -> Generator[Any, None, None]:
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fill_value, *args)


def grouper2(n: int, iterable: Iterable[T]) -> Iterator[Tuple[T, ...]]:
    """Group an iterable into tuples of length n."""
    args = [iter(iterable)] * n
    return zip(*args)


def traversal_generator(tree: T) -> Generator[T, None, None]:  # noqa
    stack: List[Any] = []

    def visit(node):
        yield node
        for child in tree.children:
            stack.append(child)
        while stack:
            yield from visit(stack.pop())

    yield from visit(tree)


# ── Utility Functions ─────────────────────────────────────────────────────────

import collections.abc as cabc
import copyreg
import inspect
import itertools
import json
import math
import os
import pstats
import re
import signal
import subprocess
import threading
import timeit
import traceback
import types
import warnings

from contextlib import contextmanager
from dataclasses import dataclass, fields, replace
from enum import Enum
from fractions import Fraction
from io import StringIO
from numbers import Number
from pathlib import Path
from pprint import pprint


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "locals":   frame.f_locals,
        "globals":  frame.f_globals,
        "constants": tuple(map(repr, frame.f_code.co_consts)),
        "filename": frame.f_code.co_filename,
        "lineno":   frame.f_lineno,
        "argcount": frame.f_code.co_argcount,
        "closures": tuple(closure.cell_contents for closure in frame.f_code.co_cellvars),
    }


def call_depth_probes() -> list[tuple[int, dict]]:
    frames: list[tuple[int, dict]] = []
    current_frame = sys._getframe()
    while True:
        try:
            d = caller_info(depth=len(frames))
            frames.append((len(frames), d))
        except ValueError:
            break
        current_frame = current_frame.f_back
    return frames[::-1]


def parsed_call_stack() -> list[inspect.FrameInfo]:
    frames = inspect.stack()[::-1][:-1]      # exclude __main__
    return [inspect.FrameInfo.fromframes(frame) for frame in frames]


# ── Garbage Collection ───────────────────────────────────────────────────────-

gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE |
             gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS |
             gc.DEBUG_SAVEALL | gc.DEBUG_STATS | gc.DEBUG_STATS | gc.DEBUG_TRACE)


# ── Tracing Memory Allocations ────────────────────────────────────────────────

tracemalloc.start(50)
snapshot = tracemalloc.take_snapshot()

for line in annotated_disassembly(hot_path(1_000)).splitlines():
    print(line.strip())
print("")

