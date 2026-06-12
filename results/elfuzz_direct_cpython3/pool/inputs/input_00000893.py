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


def load_code_from_file(
	path: str | Path, mode="r", encoding=None, errors="strict"
):
	"""Load a Python code object from a file.

	This method can be called with either `mode='r'` or `mode='rb'`.

	If `encoding` is specified, it will be passed directly to `open()`. The value
	of `errors` has no effect on the returned code object. It defaults to "strict".
	"""
	with open(str(path), mode=mode, encoding=encoding, errors=errors) as f:
		if mode == "r":
			return eval(f.read())
		elif mode == "rb":
			return compile(f.read(), path, 'exec')
		else:
			raise ValueError(f"Invalid mode {repr(mode)}")


def dump_code_to_file(code_object: CodeType, path: str | Path):
	"""Dump a Python code object to a file."""
	with open(str(path), "wb") as f:
		f.write(code_object)


# ─── LOW-LEVEL INTERPRETATION OF BYTECODE ──────────────────────────────────────

# Example values for some of the fields.
# We'll use these later in our examples below.
CO_POSONLYARG: int = 1 << 8
CO_VARARGS: int = 1 << 9
CO_VARKWARGS: int = 1 << 10
CO_COROUTINE: int = 1 << 12
CO_ITERABLE_COROUTINE: int = CO_COROUTINE | CO_ASYNC_GENERATOR
CO_ASYNC_GENERATOR: int = 1 << 13
CO_NOFREE: int = 1 << 14
CO_COROUTINE_DEF: int = CO_COROUTINE | CO_ASYNC_GENERATOR | CO_NOFREE
CO_ITERABLE_COROUTINE_DEF: int = CO_ITERABLE_COROUTINE | CO_NOFREE
CO_ASYNC_GENERATOR_DEF: int = CO_ASYNC_GENERATOR | CO_NOFREE
CO_NEWLOCALS: int = 1 << 16
CO_NESTED: int = 1 << 17


def check_co_flags(co: CodeType) -> None:
	"""Checks whether all flags make sense. Raises an exception otherwise."""
	if not (
		CO_NOFREE <= co.co_flags < 1 << 18
		and 0 <= co.co_argcount <= len(co.co_varnames)
		and 0 <= co.co_stacksize <= 2 ** 24 - 1
		and 0 <= co.co_nlocals