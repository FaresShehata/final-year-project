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
        co_firstlineno: int      # first line number for which code is valid
        co_lnotab: bytes         # mapping of line numbers to bytecode offsets
        co_freevars: tuple       # free variable names used by this function
        co_cellvars: tuple       # cell variable names used by this function


def get_python_version() -> str:
    return f"{sys.hexversion >> 24 & 0xFF}.{(sys.hexversion >> 16) & 0xFF}"


def show_memory_usage(message=""):
    print(textwrap.dedent(
        """
        Memory usage summary:
        - Peak process resident set size : {rss_mb} MB
        - Total amount of physical memory allocated : {total_physical_bytes} B
        - Amount of physical memory currently being used : {used_physical_bytes} B
        """.format(rss_mb=tm.get_traced_size(), total_physical_bytes=sys.getsizeof(tm),
                   used_physical_bytes=max(sys.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                                            sys.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)))
    )


def show_gc_stats():
    gc.set_debug(gc.DEBUG_STATS)


def get_bytes_from_file(path: Path | SupportsReadBytes):
    with path.open('rb') as stream:
        return stream.read()


def dump_bytecode(stream: BytesIO, obj: Any):
    func = getattr(inspect, 'getsource', lambda x: x.__code__.co_code)

    def write_byte_code(code_obj: CodeType):
        stream.write(func(obj))
        cc = code_obj.co_code  # byte code
        l = len(cc)
        n = 0
        while n < l:
            s = cc[n:n + 8]
            cc = cc[n+8:]
            stream.write(s)

    try:
        if isinstance(obj, types.CodeType):
            dump_bytecode(stream, obj)
        elif isinstance(obj, types.FunctionType):
            dump_bytecode(stream, obj.__code__)
        elif isinstance(obj, module):
            func = getattr(inspect, 'getsource', lambda x: x.__code__.co_code)
            dump_bytecode(stream, func(obj))
        elif isinstance(obj, types.MethodType):
            func = getattr(inspect, 'getsource', lambda x: x.im_func.__code__.co_code)
            dump_bytecode(stream, func(obj))
        elif