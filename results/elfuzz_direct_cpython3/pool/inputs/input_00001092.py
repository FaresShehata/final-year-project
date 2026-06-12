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
import os
import re
import shutil
import sys
import tempfile
import time
import types
import unittest.mock as mock
import urllib.request
from collections.abc import Iterable, Sequence
from functools import wraps
from io import StringIO
from io import TextIOWrapper
from itertools import chain, repeat, tee
from multiprocessing import Pool
from pathlib import Path
from pprint import pformat
from random import choice, randint, seed
from re import Match, Pattern, findall, split, sub
from re import escape as regex_escape
from signal import SIG_DFL, SIGINT, Signals, signal
from typing import (Any, Callable, ClassVar, Final, Generic, Literal,
                    NoReturn, Optional, Protocol, TypedDict, TypeVar)
from typing_extensions import Self, TypeGuard, Unpack
from unittest import mock as _mock
from uuid import UUID, uuid1, uuid3, uuid4, uuid5


def return_none() -> None:
    """Returns None."""
    return None


def raise_runtime_error(message: str) -> NoReturn:
    """
    Raises RuntimeError.

    Args:
        message: Error message.
    """
    raise RuntimeError(message)


def override():
    """Overrides a method."""


def add_to_list(l: list[int], n: int = 2) -> list[int]:
    """
    Add ``n`` to the list and returns the result.

    Args:
        l: List of integers.
        n: Number to add to the list.

    Returns:
        The modified list.
    """
    for i in range(n):
        l.append(1 + len(l))
    return l


def multiple_returns(*args: Any) -> tuple[bool, int]:
    """
    Return multiple values.

    For example:

    >>> multiple_returns("foo", "bar")
    (True, 'foobar')

    Args:
        args: Multiple arguments.

    Returns:
        A boolean and an integer.
    """
    if all(isinstance(arg, str) for arg in args):
        return True, "".join(args).upper()
    else:
        return False, -1


def check_types(a: int | float, b: str | tuple[str, ...]) -> bool | str:
    """
    Check types of arguments at runtime."""

    def is_string(x: object) -> bool:
        """Check if `x` is a string"""
        try:
            x.encode(encoding="utf-8").decode(encoding="ascii")
        except UnicodeEncodeError:
            return False
        except UnicodeDecodeError:
            return False
        else:
            return True

    if not isinstance(b, str):
        raise TypeError(f"{b=} should be a string")

    if type(a) == int:
        return f"Type {a} from {type(a)}"

    elif type(a) != int or type(a) != float:
        raise TypeError(f"{a=} should be either int or float")

    elif type(a) == float:
        return f"Type {a} from {type(a)}"

    elif type(a) == int:
