"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
)

import functools
import inspect
import itertools
import math
import os
import subprocess as sp
import sys
import tempfile
import textwrap
import types
import uuid
import warnings
from contextlib import contextmanager
from pathlib import Path
from pprint import pprint
from unittest.mock import Mock, patch

import pytest
from formatx import formatx
from more_itertools import flatten

from pytools.api import AllTracker, CacheCallMetaClass, groupby

# FIXME: remove once https://github.com/python/mypy/issues/5374 is fixed
if TYPE_CHECKING:
    from dicttoolkit import DictToolkit


try:
    # noinspection PyUnresolvedReferences
    import numpy as np
except ImportError:
    np = None


__all__ = [
    "b",
    "c",
    "dumps_json",
    "dump_json",
    "eq",
    "format",
    "get_attr_or",
    "get_cwd_path",
    "get_file_size",
    "get_module_for_class",
    "get_nested_attrs",
    "grab_all_attributes_of_type",
    "has_no_common_attribute",
    "lazy_dict",
    "memoize_async",
    "memoize_awaitable",
    "memoize_rec",
    "map_list",
    "throttle",
]


TR = TypeVar("T")
TA = TypeVar("TA", bound="AsyncIterator[T]")
TB = TypeVar("TB", bound="AsyncGenerator[T, T]")


@dataclasses.dataclass(order=True)
class LazyDict(Generic[TA]):
    """Lazy dictionary for use with `asyncio.Task`s.

    Example:

    >>> lazy_dict = LazyDict()
    >>> task1 = asyncio.create_task(lazy_dict.get(1))
    >>> await task1
    {}
    >>> lazy_dict[1] = {"a": 1}
    >>> task2 = asyncio.create_task(lazy_dict.get(1))
    >>> await task2
    {'a': 1}

    """

    __slots__: tuple[str] = ()
    key: str
    value: TA | AsyncIterable[Awaitable[TA]] | None = None
    parent: LazyDict[TA] | None = None

    def __post_init__(self):
        if self.value is None:
            raise ValueError("value required")

    async def get(self) -> TA:
        try:
            return self.value
        except AttributeError:
            pass
        else:
           
def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))

def is_odd_tc(n: int) -> bool:
    return not is_even_tc(n)


if __name__ == "__main__":
    print(
        "\n" +
        " ".join((
