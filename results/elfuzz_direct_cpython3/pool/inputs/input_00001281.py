"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses as dc
import enum
import itertools as it
import random
from collections.abc import Callable, Collection
from contextlib import suppress
from functools import partial
from math import ceil, floor, log10
from types import TracebackType
from typing import (
    Mapping,
    Optional,
    Protocol,
    TypeVar,
)

import pytest


def test_asyncio():
    @dc.dataclass(frozen=True)
    class Task:
        id: int
        result: float | None = None

    def task(id: int) -> Callable[[Task], bool]:
        async def _task(task_: Task) -> bool:
            if not isinstance(task_.result, float):
                return False

            task_.id += 1
            task_.result *= 2.
            await asyncio.sleep(0.)
            return True

        return _task

    loop = asyncio.get_event_loop()
    tasks: list[Task] = [
        Task(random.randint(0, 9)),
        Task(random.randint(0, 9)),
        Task(random.randint(0, 9)),
    ]

    for i in range(len(tasks)):
        tasks[i].result = random.random()

    done = []

    async def run():
        while tasks and any(map(lambda t: t.result is None, tasks)):
            pending = filter(
                lambda _: any(map(lambda t: t.id == _, tasks)),
                map(task(i), tasks),
            )
            try:
                results = await asyncio.gather(*pending)
            except KeyboardInterrupt:
                break
            finally:
                pass

            done.extend(results)

    with suppress(asyncio.CancelledError):
        loop.run_until_complete(run())

    loop.close()


# Seed 03 - Decorators and higher-order functions
def decorator(func: Callable[..., T]) -> Callable[..., T]:
    ...


def wrapper_decorator(func: Callable[..., T]) -> Callable[..., T]:
    ...


def func(a, b=2, /, c=None, **kwargs):
    ...


# Seed 04 - Generators and iterators
def gen(n: int) -> Iterator[int]:
    yield n


gen_iter = iter(gen(5))


def gen_yield(n: int) -> Generator[int, None, None]:
    yield n


gen_yield_gen = gen_yield(6)


def gen_asterisk(n: int) -> Generator[int, None, None]:
    yield* range(n)


gen_asterisk_gen = gen_asterisk(7)


@dataclass
class DataClass:
    x: int
    y: str


DATACLASS = DataClass(x=1, y='2')


def dataclass_inheritance(cls: type(DataClass)) -> type(DataClass):
    class SubDataClass(cls):
        z: int

    return SubDataClass


SUBDATACLASS = dataclass_inheritance(DataClass)


async def async_func() -> None:
    ...


def function_accepts_callable(func: Callable[..., Any]) -> None:
    ...


function_accepts_callable(async_func)


def function_returns_generic[T]() -> T:
    ...


FUNCTION_RETURNS_GENERIC = function_returns_generic[str]


async def async_function() -> None:
    ...


@pytest.mark.asyncio
async def test_async_function():
    await async_function()


def partial_func(func: Callable[..., Any], *args, **kwds):
    return partial(func, *args, **kwds)


PARTIAL_FUNC = partial_func(function_returns_generic, 'str')


async def async_partial_func(func: Callable[..., Any], *args, **kwds):
    return await partial(func, *args, **kwds)


ASYNC_PARTIAL_FUNC = await async_partial_func(function_returns_generic, 'str')


def zip_generator(iterables: Iterable[Iterable[Any]]) -> Iterator[Tuple[Any, ...]]:
    ...


ZIP_GENERATOR = zip_generator([[1, 2, 3], ['a', 'b', 'c'], [True]])


def zip_star(iterables: Iterable[Iterable[Any]]) -> Iterator[Tuple[Any, ...]]:
    ...


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

    print()
    print("-" * 80)

    print("\\\"Hello world\\\"")

    print()

    print('She said, "hello world"')

    print()

    print("""She said,
    "hello world."
	""")

    print()

    print(r'"\t"')
    print(r'"\'\n\r\t\v\f\b"'[3:-1])
    print(r'The quick brown fox jumps over the lazy dog.')
    print(r'He said, "\x01\x02\x03"')
    print(r'\t\n\f\r\v')
    print(r'\u{1F4A9}')

    print()

    print(chr(ord('"')))
    print(ord('\t'))
    print(oct(12))
    print(hex(12))

    print()

    p = Path(sys.executable)
    print(p.name)
    print(p.stem)
    print(p.suffix)
    s = Path.home().stem
    print(s[-len(str(datetime.now()))-1])

    print()

    print(Path.cwd())
    print(os.getcwd())

    print()

    print(Path.home())
    print(os.path.expanduser('~'))

    print()

    p1 = Path(__file__)
    print(p1.resolve())
    print(p1.absolute())

    print()

    print(Path('/home/user/Downloads').exists())


# Seed 02 - Time and dates
print(time.time())
