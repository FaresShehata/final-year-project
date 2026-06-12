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
import sys
import tempfile
import textwrap
import token as tok
import tokenize
import types
import typing
import urllib.parse
import warnings
import weakref
from collections.abc import Mapping, Sequence
from concurrent.futures import Future
from contextlib import (
    AbstractContextManager,
    ContextDecorator,
    suppress,
    redirect_stdout,
)
from dataclasses import InitVar
from datetime import date, datetime
from functools import partial, partialmethod
from io import TextIOWrapper
from itertools import chain, product
from operator import itemgetter
from pathlib import Path
from pprint import pprint
from random import choice, randrange
from re import Pattern
from socket import gaierror
from ssl import SSLError
from signal import SIGTERM
from sys import argv, stderr, stdin, stdout, version_info
from threading import Thread, Lock, Event
from time import sleep, time
from types import ModuleType, TracebackType
from typing import (
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Iterable,
    Iterator,
    Literal,
    NewType,
    NoReturn,
    Optional,
    Protocol,
    Reversible,
    Self,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypedDict,
    Union,
    overload,
)
from typing_extensions import (
    Concatenate,
    ParamSpec,
    TypeGuard,
    Unpack,
    NoTypingInfo,
)

__all__ = [
    "any",
    "counter",  # https://docs.python.org/3/library/threading.html#threading.Event.wait
    "defaultdict_factory",
    "enumerate",
    "get_thread_id",
    "globals_dict",
    "is_instance_of_any",
    "make_counter",
    "NoneOr",
    "no_return",
    "nonempty_iterable",
    "prefixes_and_suffixes",
    "random_password_string",
    "reversed_sequence",
    "timeout_decorator",
    "typed_dict_from_callable",
]

P_ = ParamSpec("P_")

NoneOrT = TypeVar("NoneOrT", None, TypeVar("T"))
"""A union of `None` and any type."""

IterableOfT = TypeVar("IterableOfT")
"An iterable of a type `T`."

NonEmptyIterableOfT = TypeVar("NonEmptyIterableOfT")
"""An iterable of length at least one."""

ReversibleSequenceOfT = TypeVar("ReversibleSequenceOfT")
"""A reversible sequence of a type `T`. This includes lists, tuples, strings, etc."""


def any(*values: bool) -> bool:
    """Return True if any argument evaluates to True."""
    return any(values)


@overload
def counter(iterable: None = ..., start: int = ...) -> Counter[int]:
    ...


@overload
def counter(iterable: Iterable[T], /, *, start: T = ...) -> Counter[T]:
    ...


def counter(
    iterable: Iterable[T] | None = ...,
    *,
    start: T = ...,
) -> Counter[Hashable] | Counter[T]:
    """
    Return a new Counter object, optionally initialized from an iterable.

    >>> c = counter([1, 2, 3])
    >>> print(c)
    Counter({1: 1, 2: 1, 3: 1})
    >>> c = counter(start='a')
    >>> print(c['a'])
    1
    """
    if isinstance(iterable, dict):
        return collections.Counter(iterable, **locals())
    elif not iterable:
        return collections.Counter(**locals())
    else:
        return collections.Counter(iterable, **locals())


def default_dict_factory() -> defaultdict:
    """Default factory function used when creating new dictionaries in defaultdict()."""
    return defaultdict(default_dict_factory())


def enumerate(obj: Iterable[Any]) -> Enumerator[Any]:
    """
    Make an iterator that returns sequences of two items: the index and its corresponding value.

    >>> list(enumerate('abc'))
    [(0, 'a'), (1, 'b'), (2, 'c')]
    """
    return enumerate(list(obj))


def globals_dict() -> Dict[str, Any]:
    """Return a dictionary representing the current global symbol table."""
    return vars()


def is_instance_of_any(value: object, *types: Type[Any]) -> bool:
    """
    Return True if the object is an instance of any of the given types.
    """
    return any(isinstance(value, t) for t in types)


@overload
def make_counter(iterable: None = ..., start: int = ...) -> Counter[int]:
    ...


@overload
def make_counter(iterable: Iterable[T], /from concurrent.futures.thread import ThreadPoolExecutor as ThreadExecutor
from functools import cached_property, wraps
from inspect import isawaitable, signature
from itertools import chain, repeat
from operator import itemgetter
from platform import python_implementation
from random import Random
from threading import Lock, RLock
from types import CodeType, FunctionType, ModuleType, TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    ClassVar,
    Collection,
    ContextManager,
    Counter,
    Deque,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    NamedTuple,
    NewType,
    Optional,
    Pattern,
    Tuple,
    TypedDict,
    TypeGuard,
    TypeVar,
    Union,
    cast,
)
from weakref import WeakValueDictionary

if sys.version_info >= (3, 12):
    from typing import _type_check  # type: ignore[attr-defined]
else:
    def _type_check(
        value: object,
        annotation: Any,
        detail: str = 'value',
    ) -> None:
        pass


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V', bound=numbers.Number)


# noinspection PyMethodMayBeStatic
class Seed05(unittest.TestCase):
    """Test cases for Python seed 05."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = 70_894_617_856_679_264_171_493_431_340_561_673_052_584_162_030
        cls.maxDiff = 10 ** 7

    def test_thread_lock(self) -> None:
        self.assertEqual(thread_lock(), 'test-thread-lock')

    def test_thread_executor(self) -> None:
        self.assertEqual(thread_executor(), 'test-thread-executor')

    def test_multiprocess_executor(self) -> None:
        self.assertEqual(multiprocess_executor(), 'test-multiprocess-executor')

