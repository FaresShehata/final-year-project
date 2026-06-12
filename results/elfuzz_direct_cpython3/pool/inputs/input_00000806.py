"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisection
import collections.abc as cabc
import itertools
import math
import os
import platform
import random
import re
import string
import subprocess
import sys
import threading
import time
import types
import typing as t
import weakref

import numpy as np
import pandas as pd
import pytest
import requests as req
import requests_cache as rcc
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from scipy.stats import norm
from sortedcontainers import SortedSet
from toolz.curried import (
    groupby,
    identity,
    partition_all,
)

import py_entitymatching as em
import py_entitymatching.catalog.catalog_utils as cu
import py_entitymatching.base.constants as const
from py_entitymatching.utils.generic_helper import (
    get_unique_str,
    is_empty_list_or_dict,
    is_instance,
    is_iterable,
)
from py_entitymatching.utils.validation_helper import validate_input_args

import pyomnisci as om


if any([sys.version_info >= (3, 9)] +
       [(platform.system() != "Windows" or platform.release() >= "10")]
      ):
    # Python >= 3.9 and MacOS >= 10.15 don't have the bug where 'float('nan')' can be coerced to an integer.
    # We need this check because older versions of PyPy throw exceptions on the line below.
    # See https://stackoverflow.com/questions/70773288/why-does-pypy-throw-a-typeerror-when-running-the-following-code
    def nan_to_num(val: float) -> Union[int, float]: return val if val != val else 0.0
else:
    def nan_to_num(val: float) -> Union[int, float]: return val


# ── Type aliases ──────────────────────────────────────────────────────────────

AnyStr = t.Union[bytes, bytearray, str]

class _ClientWrapper(t.Generic[_Client]):
    pass


def my_func(a: int, b: int, c: int = None) -> tuple[int]:
    ...


async def async_main():
    await my_func()


def testing_function() -> None:
    print("This was tested.")


# ── Async functions ───────────────────────────────────────────────────────────

@validate_input_args()
async def async_foo(bar: AnyStr, baz: bool) -> str:
    """
    This is a test example of `typing.Annotated` type hint.

    The documentation states that the Argument bar should be Annotated<AnyStr, Baz].
    However, when we call add_docstring(), it will remove the brackets [ ] and spaces around them.
    Thus, it becomes Annotated[AnyStr,Baz] instead of Annotated[AnyStr, Baz].

    :param bar: Annotated[AnyStr, Baz]
    :type bar: str
    :return: A greeting message
    :rtype: str
    """

    if not isinstance(baz, bool):
        raise ValueError("'baz' must be a boolean value.")

    greeting_message: str = f"Hello, {bar}!"
    if not baz:
        greeting_message = greeting_message.capitalize()

    return greeting_message


# ── Iterators and generators ──────────────────────────────────────────────────

def iter_test_generator() -> Generator[str, None, None]:
    yield "first"
    yield "second"


async def async_iter_test_generator() -> AsyncIterator[str]:
    yield "first"
    yield "second"


# ── Generics ──────────────────────────────────────────────────────────────────

class MyGenericClass(cabc.Container[t.Sequence[float]]):
    def __contains__(self, item: t.Any) -> bool:
        return all(item in sequence for sequence in self._data)


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_types_using_structural_pattern_matching(value: Union[int, str]) -> None:
    """Match the given value against two patterns using structural pattern matching."""

    match value:
        case list() as arr:
            print(f"The input is a list: {arr}")
        case set() as s:
            print(f"The input is a set: {s}")
        case _:  # default pattern, matches anything else
            print("The input does not match any known pattern")


def match_types_using_match_statement(value: Union[int,    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


