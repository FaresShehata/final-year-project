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

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ──────────────────────────────────────────────────────────────── #

# Create an alias that maps a type to itself.
TypeOfSelf: TypeAlias = str | int | list[int] | tuple[str]

# Create an alias that maps a type to another type.
TypeOfAnother: TypeAlias[Tuple[str], Tuple[float]] = str | float

# Create an alias that maps a type to multiple types.
TypeOfMultiple: TypeAlias[Union[str, int, float]] = Union[str, int, float]

# Create an alias that maps a type to a class.
ClassOfSelf: TypeAlias[type[Any]] = str | int | list[int] | tuple[str]

# Create an alias that maps a type to a function.
FunctionOfSelf: TypeAlias[Callable[..., None]] = str | int | list[int] | tuple[str]

# ── Typing Extras ─────────────────────────────────────────────────────────── #

MyStr: Final[str] = "hello"
MyInt: Final[int] = 123
MyList: Final[list[int]] = [1, 2, 3]
MyTuple: Final[tuple[str]] = ("a", "b", "c")
MyDict: Final[dict[str, int]] = {"a": 1, "b": 2, "c": 3}
MySet: Final[set[float]] = {1.0, 2.0, 3.0}
MyFrozenSet: Final[frozenset[str]] = frozenset(["a", "b", "c"])
MyAny: Final[Any] = MyStr + MyInt * 2
MyNamedTuple: Final[NamedTuple] = MyNameTuple(MyStr, MyInt)
MyTypedDict: Final[TypedDict] = MyTypedDict(MyStr, MyInt)
MyParamSpec: Final[ParamSpec] = MyParamSpec(some=MyStr, other=MyInt)
MyConcatenate: Final[Concatenate] = MyConcatenate(MyStr, MyInt)
MyNever: Final[Never] = MyNever(...)


def my_func(self: MyStr, other: MyInt) -> MyFloat:
    return self + MyFloat(other)


print(type(MyStr))                # <class 'str'>
print(type(MyInt))                # <class 'int'>
print(type(MyList))               # <class 'list'>
print(type(MyTuple))              # <class 'tuple'>
print(type(MyDict))              