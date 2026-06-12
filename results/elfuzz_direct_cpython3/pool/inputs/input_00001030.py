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
import time
import unittest.mock
import warnings
import weakref
from collections.abc import Mapping
from dataclasses import dataclass
from enum import IntEnum
from functools import cached_property
from itertools import cycle, repeat
from multiprocessing import Pool
from numbers import Number
from operator import itemgetter
from pathlib import Path
from pprint import pprint
from re import M, sub
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Sequence,
    Tuple,
    Union,
    runtime_checkable
)
from urllib.parse import quote_plus
from uuid import UUID
from weakref import ref

import asttokens
import docutils.nodes
from icontract import require, ensure, DBC
import pydantic.fields
from testtools.matchers import Equals, HasLength
from testtools.matchers import LessThan, GreaterThan
from testtools.testcase import raises, skipIf
from typing_extensions import Self, TypeGuard, NotRequired, Required, LiteralString
from typing_extensions import TypedDict as TypedDICT
from typing_extensions import Annotated as an
from typing_extensions import ParamSpec, Concatenate, TypeAlias
from typing_extensions import NoReturn, Never
from typing_extensions import Protocol
from typing_extensions import final, override, overload

from concurrent.futures import Future
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import ExecutionError
from concurrent.futures import wait
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import wait
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_EXCEPTION
from concurrent.futures import FIRST_COMPLETED
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


# ── TypedDict ────────────────────────────────────────────────────────────────

TJsonSchema = TypedDict(
    "TJsonSchema",
    {
        "type":Literal["object", "array"],
        "properties" :dict[str, TJsonSchema],
        "required" :list[str]
    },
)


# ── Enum ────────────────────────────────────────────────────────────────────

class Weekday(Final[int]):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


# ── NamedTuple ───────────────────────────────────────────────────────────────

Point = namedtuple("Point", ["x", "y"])


def my_named_tuple(*args: int) -> Point:
    return Point(x=args[0], y=args[1])

my_named_tuple(1, 2)
print(my_named_tuple.__name__)


# ── ClassVar ────────────────────────────────────────────────────────────────

class MyClass:
    __slots__ = ("_var", "_var_to_stop_after_setting", "__weakref__")
    _var: ClassVar[int] = 0
    _var_to_stop_after_setting: ClassVar[int]

    def __post_init__(self):
        assert self._var == 0
        self._var_to_stop_after_setting = 3

    @property
    def var(self):
        if self._var > self._var_to_stop_after_setting:
            raise ValueError("_var is too high!")
        return self._var

    @var.setter
    def var(self, value):
        self._var = value



# ── __getattr__, __setattr__ and __getattribute__ ───────────────────────────

class MyObj:

    _internal_var: int = 1

    def __getattribute__(self, name: str) -> object:
        if name in ('_internal_var', '__weakref__') or name.startswith('_'):
            return super().__getattribute__(name)

        print(f'Get attribute {name}')
        return self.__dict__[name]
    
    def __setattr__(self, name: str, value: object) -> None:
        if name in ('_internal_var', '__weakref__', '_secret_attribute