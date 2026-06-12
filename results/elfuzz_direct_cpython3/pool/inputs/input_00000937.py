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
import shutil
import sys
import tokens as ttokens
import tokenize
import time
import traceback
import tokenize
import types
import typing
import urllib.parse
import warnings
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from enum import EnumMeta, IntEnumMeta, auto
from functools import partialmethod
from itertools import product, starmap
from operator import methodcaller
from platform import python_implementation
from re import compile, match, sub
from string import Formatter as StringFormatter
from subprocess import check_output
from threading import Thread, Event
from time import sleep
from typing import (
    Any,
    Callable,
    ClassVar,
    Collection,
    ContextManager,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeAlias,
    TypedDict,
    Union,
    Var,
    cast,
    overload,
)

warnings.filterwarnings("ignore")

# _____________________________________________________________________________


def _seed_data():
    return [
        b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"
        + b"\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001a"
        + b'\u001b\u001c\u001d\u001e\u001f !"#$%&\'()*+,-./'
        + b'0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\r\n',
        b'aA\b\f\v\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10'
        + b'\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001a'
        + b'\u001b\u001c\u001d\u001e\u001f !"#$%&\'()*+,-./'
        + b'0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\r\n',
        b"a '\n\x80-\x9f\xad-\xbf\xef-\xff",
    ]


# _____________________________________________________________________________

T = TypeVar('T')
AnyStr = Union[str, bytes]


def _special_repr(obj: T) -> T:
    if hasattr(obj, "__repr__"):
        repr_str = getattr(obj, "__repr__")()
        try:
            obj.__repr__.__wrapped__(repr_str())
        except Exception:
            pass
    return obj


def _base_repr(obj: object) -> str:
    """Like `object        MyThread(target=lambda x="x": x.upper(), name=f"t{i}")
        for i in range(10)
    ]
    [thread.start() for thread in threads]
    finish_event = Event()
    # first argument is a callable that takes no arguments and does nothing
    # except setting the event flag to True when called. Otherwise, this is an
    # empty function.
    [thread.join(1) or finish_event.set() for thread in threads]
    finish_event.wait()

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_thread_names = {
            executor.submit(lambda x="x": x.upper(), name=f"{i}"): f"{i}"
            for i in range(10)
        }
        results = dict(
            map(cast(Callable[[Future[str]], str], future_thread_names.pop),
                filter(None.__ne__, executor.map(methodcaller("__name__"),
                                                 future_thread_names))))
    assert set(results.values()) == {"t0", "t1", "t2", "t3", "t4", "t5",
                                      "t6", "t7", "t8", "t9"}

    with ProcessPoolExecutor(max_workers=10) as