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
import subprocess
import time
import tokenize
import types as pytypes
import unicodedata
from collections.abc import Iterator, Mapping, Sequence
from datetime import timedelta
from functools import wraps
from operator import attrgetter
from queue import Queue
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    TypedDict,
    TypeVar,
    cast,
)
from weakref import ref
from zipfile import BadZipFile

# noinspection PyPackageRequirements
from _pytest.compat import is_pytest_runner, PathLike

try:
    from _multiprocess_freeze import FREEZE
except ImportError:
    FREEZE = False


if is_pytest_runner():
    # noinspection PyUnresolvedReferences
    import pytest
else:
    # noinspection PyUnresolvedReferences
    import doctest

if FREEZE:
    from .._freeze import FrozenModule
    from .seed_01 import seed
else:
    from ... import seed
    from ._utils import assert_equal

# noinspection PyUnusedLocal
from typing_extensions import (
    ParamSpec,
    Concatenate,
    TypeAlias,
    Never,
    Annotated,
)

T = TypeVar("T")
Self = TypeVar("Self", bound="NamedTuple")


def test_isinstance():
    class A(NamedTuple):
        a: int

    class B(A):
        b: float

    assert isinstance(B(2, 3), B)
    assert not isinstance(B(2, "a"), B)


def test_namedtuple_starred_field():
    """
    >>> A = namedtuple('A', 'a')
    >>> A.__new__.__defaults__
    ()

    >>> B = namedtuple('B', ['a'])
    >>> B.__new__.__defaults__
    ()
    """

    class A(NamedTuple):
        a: int

    class B(NamedTuple):
        a: int

    assert A._field_types == {}
    assert B._field_types == {"a": int}


def test_namedtuple_equality():
    assert NamedTuple() != NamedTuple()
    assert NamedTuple(a=1) != NamedTuple()

    class A(NamedTuple):
        a: int

    assert A(1) == A(1)
    assert A(1) != A(2)

    class B(NamedTuple):
        a: tuple[int, int]

    assert B((1, 2)) == B((1,
    @overload
    @classmethod
    def parse_many(cls, *args: str | Self) -> list[Self]: ...
    @overload
    @classmethod
    def parse_many(cls, iterable: Iterable[str | Self]) -> list[Self]: ...

    @classmethod
    def parse_many(cls, *args: str | Self) -> list[Self]:
        return [cls.parse(x) for x in args]

    @classmethod
