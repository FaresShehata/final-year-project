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
    TypedDict,
    Union,
    cast,
)
from weakref import WeakValueDictionary
from zlib import adler32


def seed05() -> int:
    """Example of concurrent.futures and string formatting."""

    class MyThread(Thread):
        def run(self) -> None:
            print("Starting thread", self.getName())

    threads = [
        MyThread(target=lambda x="x": x.upper(), name=f"t{i}")
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