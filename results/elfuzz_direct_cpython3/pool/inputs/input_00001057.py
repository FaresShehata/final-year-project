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
import re
import signal
import sys
import time
import threading as pyth_tread
import tokenize as python_tokenize
import types
import unittest.mock
import uuid
import weakref
from abc import abstractmethod
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import suppress, redirect_stdout, AbstractContextManager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import partial, singledispatch
from glob import glob
from inspect import getmembers, signature, Parameter, isroutine, unwrap, cleandoc
from itertools import count, cycle
from operator import attrgetter
from pathlib import Path
from pickle import loads, dumps
from pprint import PrettyPrinter
from random import randrange, sample, choice
from reprlib import recursive_repr
from re import escape
from re import Pattern as re_Pattern
from re import search, match, findall, sub, split
from re import IGNORECASE as RE_FLAG_IGNORECASE
from re import DOTALL as RE_FLAG_DOTALL
from re import MULTILINE as RE_FLAG_MULTILINE
from re import VERBOSE as RE_FLAG_VERBOSE
from shutil import disk_usage, rmtree, which
from subprocess import run, PIPE
from statistics import mean, median, stdev
from string import Template, Formatter, ascii_letters, punctuation
from tempfile import mkstemp, TemporaryDirectory, NamedTemporaryFile, SpooledTemporaryFile
from time import sleep, monotonic
from types import FunctionType, CodeType, MethodType, ModuleType, TracebackType
from typing import (Any, AnyStr, Callable, ClassVar, Collection, Container, Dict, Generic,
                    Hashable, Iterable, Iterator, List, Mapping, MutableMapping, NewType,
                    Optional, Sequence, Set, Tuple, Type, TypeVar, Union, NoReturn, cast,
                    overload, runtime_checkable)
from typing_extensions import (Annotated, ParamSpec, Concatenate, TypeAlias, Never,
                               Final, Protocol, Literal, Self, TypedDict, get_origin,
                               get_args, get_type_hints, reveal_type, get_running_library_module)

if __debug__:
    from test.support import TESTFN


def _test() -> None:
    # Seed 01 - String formatting and i/o
    print(f"{int(2.7)}")
    print("a" + "b")
    assert "abc"[1] == "b"
    assert [1, 2][1:] == [2]
    assert {1: 2}[1] == 2
    assert {**{"1": 2}, **{"3": 4}} == {"1": 2, "3": 4}
    assert range(3).count(2) == 1
    assert complex(1, 2).__complex__() == 1j
    assert complex(1j).__float__() == 1.0
    assert round(1 / 3, ndigits=2) == 0.33
    assert sum([1, 2, 3]) == 6
    assert sorted({1, 2, 3}) == [1, 2, 3]
    assert any([True, False, True])
    assert all([False, False, False]) == False
    assert max([1, 2, 3])
    assert min([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3]

    print(f"{None!s}")
    print(f"{1234567890!:x}")
    print(f"{1234567890:,}")

    assert bytes.fromhex("1234") == b"\x12\x34"

    print(repr(bytes(b'\xf0\x9f\xa4\x96')))  # Unicode emoji
    print(fr'Hello\nWorld')

    print(f'''Hello
World''')
    print(f"""Hello
World""")

    print(str.encode('hello', 'utf-8'))
    print(bytes.decode(b'\xc3\xb6\xc3\xbc\xc3\xa4\xc3\xa4', 'latin1'))

    assert compile(r"(?m)^foo.*$", "re", "X").flags & RE_FLAG_DOTALL
    assert compile(r"(?sm)^foo.*$", "re", "U").flags & RE_FLAG_MULTIILINE
    assert compile(r"(?ms)^foo.*$", "re", "L").flags & RE_FLAG_LCASE
    assert compile(r"^(?i)foo(?-i)", "re", "V").flags & RE_FLAG_VERBOSE

    print((compile(r"^foo", "re", "U")).pattern.pattern)
    print((compile(r"^foo", "re", "U")).flags)

    assert compile(r"(?m)^foo$").match("\nfoo\nbar") is None
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
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    assert isinstance(value, constraint), \
                        f"{self.pub}: {value!r} does not satisfy `{constraint}`"
        setattr(obj, self.priv, value)


def positive_integer(_: Annotated[int, Predicate(lambda x: x > 0)]):
    return _


def non_negative_float(_: Annotated[float, Predicate(lambda x: x >= 0)]):
    return _

def no_duplicates(
    _: Annotated[list[Any], 
              Predicate(lambda l: len(l) == len(set(l)))]):
    return _


def unique_keys(
    _: Annotated[dict[str, Any], 
                 Predicate(lambda d: len(d.keys()) == len(set(d.keys())))]):
    return _


# ── _AnnotatedMetaData ───────────────────────────────────────────────────────

class _AnnotatedMetaData(Generic[T]):
    """Metadata for annotated types.
    
    A type annotation with a `__metadata__` attribute.
    """

    __slots__: tuple[str, ...] = ("_constraints", )

    def __init__(self, *constraints: Predicate[Any]) -> None:
        self._constraints = tuple(constraints)

    @property
    def __metadata__(self) -> tuple[Callable[[Any], bool]]:
        return self._constraints

# ── Annotated ────────────────────────────────────────────────────────────────

class Annotated(_AnnotatedMetaData[T]):
    """Class-based Annotated type.

    Supports nested and multiple decorators, similar to typing.Annotated.
    """

    __slots__: tuple[str, ] = ()

    @_AnnotatedMetaData.register
    class _AnnotatedMeta(type[_T]):
        """Annotated metaclass."""
        
        def __new__(cls, name, bases, namespace, **kwargs: Any) -> _AnnotatedMeta:
