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
import sys
import threading
import types
import typing
import uuid
import warnings
import weakref
import zlib
from collections.abc import AsyncGenerator, Generator, Sequence, Sized
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from functools import cache, lru_cache, wraps
from itertools import count, cycle, islice, tee, zip_longest
from operator import attrgetter, itemgetter
from platform import python_version_tuple
from re import Pattern, compile, finditer, subn
from signal import SIGINT, SIGTERM, Signals
from socket import AF_INET, SOCK_STREAM, SHUT_RDWR, error as SocketError
from subprocess import PIPE, Popen, TimeoutExpired, check_output
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from threading import Event, Lock, Thread
from textwrap import dedent
from time import perf_counter_ns, sleep
from types import TracebackType
from typing import TYPE_CHECKING, Any, NoReturn, Self, SupportsBytes, SupportsFloat
from urllib.request import urlopen
from zlib import compressobj, decompressobj

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
    from types import FrameType
else:
    def _typecheck(obj):
        if not isinstance(obj, type(obj)):
            raise TypeError(f"expected an instance of the given type")
        return obj


T = TypeVar("T")

P = ParamSpec("P")


class MyEnum(Enum):
    """An example class."""

    ONE = 1
    TWO = 2


class A:
    pass


class B(A):
    pass


class C(B):
    pass


def my_function(a: A | B | C) -> bool:
    """A function that accepts any one of its arguments' classes.

    Note that this uses the special `|` operator to specify multiple possible
    argument types.
    """
    return True


class MyClass:
    """Class with methods and attributes."""

    def method(self, arg1: str, arg2: int = 42) -> None:
        ...

    @property
    def property(self) -> int:
        ...

    @staticmethod
    def static_method(arg1: str, /, *, kwarg1: int) -> bool:
        ...

    @classmethod
    def class_method(cls, arg1: str, /, *, kwarg1: int) -> bool:
        ...

    @classmethod
    def class_method_with_positional_args_and_kwonlyargs(
        cls, arg1: str, arg2: int, *, kwarg1: int
    ) -> bool:
        ...


class Number(MyEnum):
    ZERO = 0
    ONE = 1
    TWO = 2


if TYPE_CHECKING:
    from typing_extensions import Self


# Match
from enum import Enum
from typing import Literal, Union

Status = Literal["PENDING", "SUCCESS", "FAILED"]


class StatusEnum(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


if __name__ == "__main__":
    # Match on enums
    if StatusEnum.PENDING.value != Status.PENDING:
        print("OK")

    if StatusEnum[Status.PENDING] == StatusEnum.PENDING:
        print("OK")

    match StatusEnum.PENDING:
        case StatusEnum.PENDING:
            print("Pending")
        case StatusEnum.SUCCESS:
            print("Success")
        case StatusEnum.FAILED:
            print("Failed")

    match Number(3):
        case Number.ZERO:
            print("Zero")
        case Number.ONE:
            print("One")
        case Number.TWO:
            print("Two")

    # Match on union type
    match 3:
        case Number.ONE | Number.TWO:
            print("Number is either One or Two")
        case _:
            print("Number is neither One nor Two")
    match 3.0:
        case Number.ONE | Number.TWO:
            print("Number is either One or Two")
        case _:
            print("Number is neither One nor Two")

    # Match on attribute access on object
    x: dict[str, int] = {}
    y: list[dict[str, int]] = []
    z: set[dict[str, int]] = set()
    match x:
        case dict.get(x, "foo"):
            print("x has a foo attribute")
        case dict.get(y, "bar"):
            print("y has a bar attribute")
        case dict.get(z,            print(f"Name: {name}, Age: {age}")
            for key, value in props.items():
                print(f"{key}: {value}")


def match_enum(status: Status):
    match status:
        case Status.PENDING:
            print("Pending")
        case Status.SUCCESS:
            print("Success")
        case _ as other_status:
            print(other_status.value)


def match_tuple(tuple_thingy: tuple[int, ...]):
    match tuple_thingy:
        case [first, second]:
            print(f"{first} and {second}")
        case [first, *rest]:
            print(first)

        self.status = Status.RUNNING
        try:
            result = asyncio.run(self.func())
        except BaseException as exc:
            self.status = Status.FAILED
            raise exc
        else:
