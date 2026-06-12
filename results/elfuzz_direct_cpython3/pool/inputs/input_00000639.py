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
) -> CodeType | PyCodeAttributes:
	with open(path, mode=mode, encoding=encoding, errors=errors) as fp:
		return load(fp)


if sys.version_info >= (3, 10):

	if _TypedDict is not None:

		def dump_attributes(obj: PyCodeAttributes) -> PyCodeAttributes:
			return obj

	else:

		def dump_attributes(obj: PyCodeAttributes) -> dict[str, Any]:
			return {k: v for k, v in obj.items()}  # noqa: E731


else:

	dump_attributes = lambda obj: obj.__dict__

dump_code = partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)

try:  # pragma: no cover
	import cProfile as profile
except ImportError:  # pragma: no cover
	try:  # pragma: no cover
		import profile as profile
	except ImportError:  # pragma: no cover
		pass  # pragma: no cover


def profile(func: Callable[..., Any]) -> Callable[..., Any]:  # pragma: no cover
	"""Profile a function."""
	return func

profile_docstr = """
.. autofunction:: profile
"""


class Profile(profile.Profile):  # pragma: no cover
	"""A custom profile class."""


def print_profile_stats() -> None:  # pragma: no cover
	prof.print_stats(sort=-1)

print_profile_docstr = """
.. autofunction:: print_profile_stats
"""


class MyProfile(Profile):  # pragma: no cover
	"""MyProfile class.

	This class inherits from :py:class:`_cProfile.Profile`.
	"""

	def run(self, count=1):  # pragma: no cover
		self.runcall(super().run, count=count)

myprofile_docstr = """
.. autoclass:: myprofile_docstr
	:members:
"""


class MyProfile(MyProfile):  # pragma: no cover
	"""MyProfile class.

	This class inherits from :py:class:`Profile`.
	"""

	def clear(self, *args):  # pragma: no cover
		super().clear(*args)

myprofile_docstr = """
.. autoclass:: myprofile_docstr
	:members:
"""


def profile_func(func: Callable[..., Any], nruns=1) -> Callable[..., Any]:  # pragma: no cover
	"""Profile a function withfrom inspect import Attribute, Parameter, signature
from itertools import chain
from keyword import iskeyword
from math import log
from operator import attrgetter, itemgetter
from pathlib import Path
from pprint import PrettyPrinter
from pyrsistent import PClass, field, pmapfield, pvectorfield, persistent
from typing import (
	Any, AnyStr, Callable, ClassVar, Dict, Generic, Hashable, IO, Iterable,
	List, Literal, Mapping, Match, NoReturn, Optional, Pattern, Sequence,
	Set, SupportsIndex, Tuple, Type, TypedDict, Union, get_args, get_origin,
	get_type_hints, overload, runtime_checkable, TypeGuard, TypeVar,
	TypeVarTuple, VarArg, VarKwArg, _SpecialForm, _T_co, _T_contra,
	_AnyTypeVars, _InferGenericArgs, _Protocol
)
from weakref import ref
import tokenize
#from textwrap import dedent
from typing_extensions import TYPE_CHECKING, ClassVar, Self, TypeAlias
from typing_inspect import is_typeddict_v2, is_union_type, get_args as ti_get_args
import contextlib
import csv
import datetime
import filecmp
import fnmatch
import fcntl
import functools
import heapq
import importlib.util
import ipaddress
import itertools
import json
import keyword
import linecache
import locale
import logging
import lzma
import mmap
import mimetypes
import multiprocessing
import os
import platform
import random
import reprlib
import signal
import shutil
import socket
import sqlite3
import subprocess
import sysconfig
import tarfile
import tempfile
import textwrap
import threading
import time
import token
import tokenize
import tokenize2
import traceback
import types
import uuid
import warnings
import zipfile

import concurrent.futures
import contextlib
import contextvars
import copyreg
import doctest
import email.message
import errno
import html.parser
import http.client
import http.cookiejar
import http.server
import http.cookies
import httplib	/**
	 * Whether or not the person is a student.
	 */
	is_student: bool
"""

JsArray: TypeAlias = List[JsObject]

js_obj_str: JsonStr = """[
    {
        "name": "John",
        "age": 30,
        "city": "New York"
    },
    {
        "name": "Jane",
        "age": 28,
        "city": "London"
    }
]"""

# type aliases for JSON object and array

JsonObj: TypeAlias = Dict[str, Any]
JsonArr: TypeAlias = List[Any]


def main() -> None:
	print("seed 05")


if __name__ == "__main__":
	main()


print(__doc__)