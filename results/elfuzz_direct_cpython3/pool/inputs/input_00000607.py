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
    "iter_path",
    "json_dump_to_file",
    "list_from_csv",
    "path",
    "print_bytearray_hex_string",
    "repr_bytes",
    "reraise",
    "round_half_up",
    "round_away_from_zero",
    "shuffled",
    "sleep_for",
    "sort_with_key",
    "sorted_by_keys",
    "split_text_in_lines",
    "special_characters",
    "to_tuple",
    "tuples_from_list",
    "type_checkers",
]


######################################################################
#
# Loop Traps
#

class LoopTrap(Generic[T]):  # pragma: no cover
    """
    A decorator that catches `KeyboardInterrupt` exceptions while executing a coroutine.

    In that case, it raises a `LoopTrapped` exception.
    """

    def __init__(self, func: Callable[..., T], /):
        self.func = func
        self._loop_guard = None

    async def __call__(
        self,
        stop_event: Event,
        timeout: float = 0.1,
        *,  # force keyword arguments
    ):
        """
        Execute the decorated coroutine until either the event loop is stopped or the timeout elapses.
        """
        self._loop_guard = _LoopGuard(timeout)
        await self._run(stop_event)
        self._loop_guard.stop()

    async def _run(self, stop_event: Event):
        try:
            await self.func(*stop_event.wait())
        finally:
            stop_event.clear()


@overload
def any(iterables: Iterable[Any] | None = ...) -> bool:
    ...


@overload
def any(predicates: Iterable[Callable[[Any], bool]] | None = ...) -> bool:
    ...


def any(iterables_or_predicates: Iterable[Any] | None = (), **kwargs):
    """
    Return ``True`` if any element of iterable evaluates to ``True``, otherwise ``False``.

    If passed no argument, returns ``False``. If only one argument is given, returns ``pred(arg)``
    for the first element of the argument sequence; otherwise, returns ``pred(arg1, arg2, ...)``.

    If optional parameter default is specified, and no elements evaluate to False, the default value
    is returned.
    """
    if kwargs:
        pred = kwargs["predicate"]  # type: ignore
    elif iterables_or_predicates:
        iterables = iterables_or_predicates

    result = False

class BoringException(Exception):
    pass


def dummy():
    """This function is used to make the example more readable."""
    return "dummy"


def run():
    """main entry point"""
    print("##############################")
    print("#         Seed 02            #")
    print("##############################\n")

    print("asyncio")
    a = asyncio.run(asyncio.sleep(1))
    assert a == 1.0

    print("\ndataclasses")
    @dataclasses.dataclass()
    class Point:
        x: int
        y: int
        z: int | None = None

    p = Point(x=2, y=4)
    print(p)  # -> Point(x=2, y=4, z=None)

    @dataclasses.dataclass(order=True)
    class Person:
        name: str
        age: int

    person1 = Person('John', 25)
    person2 = Person('Alice', 30)
    person3 = Person('Bob', 28)

    print(person1 < person2)  # -> True

    person_dict = {'name': 'John', 'age': 25}
    person = Person(**person_dict)
    print(person.name)  # -> John

    print('\nprotocols')
    if isinstance(None, Enum):  # type: ignore
        raise TypeError('None cannot be an instance of enum.Enum')

    @enum.unique
    class Suit(enum.Enum):
        HEARTS = '\N{BLACK HEART SUIT}'
        DIAMONDS = '\N{BLACK DIAMOND SUIT}'

    suit = Suit.HEARTS
    print(suit.value)  # -> ♥

    print('\ndataclasses.__slots__')
    @dataclasses.dataclass(slots=True)
    class Vector2D:
        x: float
        y: float

    v = Vector2D(1.0, 1.0)
    try:
        v.z = 1.0
    except AttributeError as err:
        print(err.__cause__)  # -> '_SlotAssignmentError'
        print(err.args[0])  # -> 'Vector2D' object has no attribute '__dict__'

    print('\ndataclasses.__annotations__ and type hints')
    @dataclasses.dataclass(init=False, kw_only=True, slots=True)
    class Movie:
        title: str
        year: int
        rating: float

    movie = Movie(title='Matrix', year=1999, rating=5.1)
    print(movie.rating)  # -> 5.1

    print('\ntype aliases')
    T = TypeVar('T')


    def normalize(value: T, minimum: T, maximum: T) -> T:
        delta = (maximum - minimum)
        if delta == 0:
            raise ValueError(f"Minimum ({minimum}) must not be equal to maximum ({maximum})")
        normalized_value = ((value - minimum) / delta * 100)
    shapes = [Circle(radius=2), Square(side_length=3)]
    for shape in shapes:
        match shape:
            case Square(side_length=sq_side):
                print(f"A square with side length {sq_side}")
            case Circle(radius=c_radius):
                print(f"A circle with radius {c_radius}")

   