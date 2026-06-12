"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup


    - async/await
        * async generator
        * awaitables (generators and coroutines)
        * async context managers

    - Protocols
        * rich comparison protocol
            > https://docs.python.org/3/library/typing.html#rich-comparison-protocols
        * sequence protocols
        * mapping protocols
        * set operations (e.g. intersection)

    - data classes
        * @dataclass
        * default_factory
        * fields() method

    - slots
        * __slots__
        * namedtuple.__new__()

    - structural pattern matching
        * match case

    - walrus operator
        * :=

    - typing generics
        * Generic[T]

    - exception groups
        * ExceptionGroup

    - Walrus operator 🎈
"""

import asyncio
from collections import defaultdict
import dataclasses
import enum
import functools
import itertools
import json
import logging
import os
import pathlib
import random
import re
import socket
import subprocess  # nosec B404
import sys
import threading
import time
import types
import typing
import uuid
import warnings
import weakref
import zlib
from abc import ABCMeta, abstractmethod
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Callable,
    Collection,
    Container,
    Hashable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Sized,
    ValuesView,
)
from collections.abc import Generator
from decimal import Decimal
from fractions import Fraction
from functools import partial
from heapq import heappushpop
from itertools import accumulate, chain, combinations, cycle, groupby, product, repeat, starmap, tee, zip_longest
from math import ceil, log1p
from operator import attrgetter, itemgetter, methodcaller
from pickle import dumps, loads
from platform import node
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from signal import SIGINT
from statistics import mean, median
from string import ascii_uppercase, digits, printable
from typing import (
    Any,
    AbstractSet,
    Awaitable,
    BinaryIO,
    Coroutine,
    ClassVar,
    Counter,
    Deque,
    Dict,
    FrozenSet,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeAlias,
    TypeGuard,
    TypedDict,
    Union,
    overload,
    runtime_checkable,
)
from unittest.mock import Mock
from uuid import UUID

from _statsmodels.datasets.eshun import eshun_data
from base64

def generator_expression() -> Generator[int]:
    return (n + 1 for n in range(10))


@overload
def consume(gen: Iterable[object]) -> None:
    ...


@overload
def consume(gen: Iterator[object]) -> object | None:
    ...


def consume(gen):  # type: ignore[misc]  # returns different things depending on whether it's an iterator or not
    try:
        return next(gen)
    except StopIteration as e:
        return e.value


def stream(func: Callable[..., Generator], /, *args):
    gen = func(*args)
    result = consume(gen)
    while result is not None:
        print(result)
        result = consume(gen)


stream(count_down, 5)  # prints from 5 down to 0
stream(generator_expression)  # prints the values yielded by the generator expression


# ── more generators ───────────────────────────────────────────────────────────

def count_up_to(n: int) -> Generator[int, None, None]:  # generators can also have a final value
    i = 0
    while i < n:
        yield i
        i += 1


def count_down_to(n: int) -> Generator[int, None, None]:  # generatorsdef unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

