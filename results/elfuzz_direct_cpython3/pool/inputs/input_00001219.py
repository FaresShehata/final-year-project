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
import random
import secrets
import signal
import struct
import tempfile
import time
import tokenize
import types
import unittest
import threading
import urllib.parse
from collections.abc import Iterable, Callable, Generator, Sequence
from concurrent.futures import ThreadPoolExecutor as FuturePoolExecutor
from concurrent.futures._base import CancelledError
from contextlib import suppress, redirect_stdout, AbstractContextManager
from functools import partialmethod, reduce
from operator import itemgetter
from pathlib import Path
from pickle import PicklingError, UnpicklingError
from secrets import token_bytes
from tempfile import TemporaryDirectory
from typing import (
    Any,
    TYPE_CHECKING,
    Union,
    Optional,
    Tuple,
    List,
    Set,
    Dict,
    Deque,
    NamedTuple,
    Literal,
    overload,
    Iterator,
    cast,
    IO,
    ClassVar,
)
from uuid import UUID, uuid4
from warnings import warn

if TYPE_CHECKING:
    from datetime import timedelta


def ignore_resource_warning(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to silence ResourceWarning by ignoring it to avoid spamming
    user with too many messages.

    Example::

        @ignore_resource_warning
        def my_func():
            ...

    See Also:
        https://docs.python.org/3/library/warnings.html#resourcewarning
    """

    @overload
    def decorator(
        func: Callable[..., Any], *, message: str = "ResourceWarning"
    ) -> Callable[..., Any]:
        ...

    @overload
    def decorator(
        *args: Any, **kwargs: Any, /, *, message: str = "ResourceWarning"
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        ...

    def decorator(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        if isinstance(args[0], type):
            return _decorator_aux(*args, **kwargs)

        def _decorator_aux(f: Callable[..., Any]) -> Callable[..., Any]:
            return _decorator(f, **kwargs)

        return _decorator_aux

    def _decorator(f: Callable[..., Any], *, message: str = "ResourceWarning") -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except ResourceWarning:
                # pylint: disable=raise-missing-from
                raise
            finally:
                pass

        return cast(Callable[..., Any], wrapper)

    return cast(Callable[..., Any], decorator)


def _decorator_aux(
    func: Callable[..., Any],
    *,
    handler: Callable[[Any], None] | None = lambda exc_info: print(exc_info),  # noqa: B912
) -> Callable[..., Any]:
    """Implementation of the decorator."""

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        with suppress(ResourceWarning):
            return func(self, *args, **kwargs)

    return cast(Callable[..., Any], wrapper)


@_decorator_aux(message="MemoryWarning")
def ignore_memory_warning(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorate a function to suppress MemoryWarnings."""
    return func


def _format_exc_with_traceback() -> str:
    """Return formatted traceback and exception information."""
    info = sys.exc_info()
    with StringIO() as buf, redirect_stderr(buf):
        traceback.print_exception(*info)
        tb_text = buf.getvalue()

    return "\n".join((str(info[0]), str(info[1]), tb_text))


def copy_except_attr(obj: object, attr_names: Iterable[str]) -> object:
    """
    Return a deep copy of `obj` excluding specified attributes.

    If an attribute is not available on `obj`, then it won't be copied.
    """
    result = copy.deepcopy(obj)
    for name in attr_names:
        setattr