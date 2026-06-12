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
import timeit
import types
import typing
import typing_extensions as te
import urllib.parse
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import (
    MutableMapping,
    Sequence,
)
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from itertools import chain, cycle, tee
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import sample
from re import Pattern
from sys import argv
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
)
from uuid import UUID


def _check_non_none(obj: object, name: str) -> None:
    if obj is None:
        raise TypeError(f"{name} must be a non-None value")


# Exceptions.


class BadFormat(Exception):
    pass


# Data structures and iterators.


class Suffixes(NamedTuple):
    """Suffixes for each character of the alphabet."""

    lower: str = "abcdefghijklmnopqrstuvwxyz"
    upper: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits: str = "0123456789"


# Classes and functions.


def check_positive(value: int | float) -> None:
    """Check that `value` is positive."""
    if not value > 0:
        raise ValueError("must be positive")


def check_neg_or_zero(value: int | float) -> None:
    """Check that `value` is negative or zero."""
    if not value >= 0:
        raise ValueError("must be negative or zero")


def chunked(iterable: Iterable[Any], n: int, *, fillvalue: Any = None) -> Iterator[List]:
    """Iterate over chunks of length `n`, optionally filling remaining with `fillvalue`.

    >>> list(chunked([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def count_to(n: int) -> Iterator[int