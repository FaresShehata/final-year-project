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
import os
import re
import secrets
import shutil
import sys
import tempfile
import threading
import tokenize
import types
import time
import traceback
import urllib.parse as urlparse
import uuid
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import Iterable, Iterator, Sequence, Callable
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial, wraps, lru_cache, singledispatchmethod
from inspect import signature, Parameter, isawaitable, AsyncGenerator, iscoroutinefunction
from io import TextIOWrapper
from itertools import chain
from logging import getLogger, CRITICAL, WARNING, ERROR
from operator import itemgetter
from pprint import pformat
from random import choice, randint
from re import Pattern
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from typing import (
    Any,
    overload,
    Awaitable,
    NoReturn,
    Optional,
    Union,
    Tuple,
    List,
    Dict,
    Generator,
    Deque,
    Set,
    FrozenSet,
    ClassVar,
    Mapping,
    Counter,
    Generic,
    Protocol,
)
from typing_extensions import Literal, TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Annotated, get_args, get_origin, _AnnotatedAlias, get_origin, get_args
from typing_extensions import Self, ParamSpecArgs, ParamSpecKwargs, ParamSpecArgsKwargs, TypeGuard, Unpack, TypeAlias
from weakref import ref, WeakKeyDictionary


from .utilities import (
    html_escape,
    html_unescape,
    parse_url,
    set_trace,
    yellow,
    green,
    red,
)

log = getLogger(__name__)


BYTES_TYPE: TypeAlias = "bytearray | MemoryView"
STR_TYPES: TypeAlias = "str | bytes | bytearray | memoryview"


# ── Miscellaneous utilities ───────────────────────────────────────────────────


# ── Context managers ───────────────────────────────────────────────────────────


class SuppressException(Exception):
    pass


def suppress(*exceptions: Exception) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator that suppresses exceptions during function execution.

    Args:
        *exceptions: The exception types to be suppressed.
    """

    def decorator(func: Callable[..., Any]) -> Any:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except exceptions as exc:
                raise SuppressException(exc) from None

        return wrapper

    return decorator


@overload
async def suppress_return(
    func: Callable[[], Awaitable[Any]]
) -> Tuple[NoReturn, Callable[[], Awaitable[Any]]]: ...

@overload
async def suppress_return(func: Callable[..., Awaitable[Any]]) -> Tuple[Any, Callable[..., Awaitable[Any]]]: ...

async def suppress_return(func: Callable[..., Awaitable[Any]]) -> Tuple[Any, Callable[..., Awaitable[Any]]]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            raise SuppressException(exc) from None
        finally:
            return None
    
    return None, wrapper


class RedirectStdStreams:
    """Redirect stdout/stderr to files."""

    def __init__(
        self, *, out_path: str, err_path: Optional[str] = None
    ) -> None:
        self.out_file = open(out_path, mode="w")
        self.err_file = open(err_path or out_path, mode="w") if err_path else None

    def __enter__(self) -> None:
        self
def dump_bytes(bytes_obj: bytes) -> None:
    """Dump the contents of a bytes-like object to standard output."""
    for byte in bytes_obj:
        print(byte, end=" ")
        if byte < 32 or byte > 127:
            print(" ", end="")
        print(chr(byte) if 32 <= byte < 127 else ".", end="")
    print("\n")


def cast_pointer(ptr: int, length: int) -> ctypes.Array:
    """Cast an integer pointer to a ctypes array of specified length."""
    return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_char * length)).contents


def array_as_buffer(array: array.array) -> bytes:
    """Convert an array to a plain bytes instance."""
    ptr = id(array.buffer_info()[0])
    length = array.itemsize * array.nbytes
    return cast_pointer(ptr, length).raw


# ── Struct — binary
# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
