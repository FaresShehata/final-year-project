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
    Sized,
    Tuple,
    Type,
    TypeAlias,
    TYPE_CHECKING,
    TypedDict,
    Union,
    cast,
    overload,
)
from unittest.mock import patch, Mock
from uuid import UUID, uuid1
from weakref import ref, WeakSet, WeakKeyDictionary


def _print(*args: str, sep: str = " ", end: str = "\n"):
    print(f"seed_05.{args[0]}", *args[1:], sep=sep, end=end)


# -----------------------------------------------------------------------------
# Concurrency (threading/multiprocessing/concurrent.futures)

_print("Concurrency")

_thread_locks: dict[type[WeakReference[Any]], type[Lock]] = {}


@overload
def lock_for(klass: None = None, /) -> None:
    ...


@overload
def lock_for(klass: ClassVar[type[WeakReference[Any]]], /) -> type[Lock]:
    ...


def lock_for(
    klass: ClassVar[type[WeakReference[Any]]]
    | None = None,
    /,
):
    """Returns a class-unique lock for the given class."""
    if klass is None:
        return None
    elif isinstance(klass, type):
        try:
            return _thread_locks[klass]
        except KeyError:
            lock = Lock()
            _thread_locks[klass] = lock
            return lock
    else:
        raise TypeError("_lock() expected a class")


_print("Thread locking")

with lock_for():
    with lock_for():
        pass

assert lock_for().__class__ == Lock

_thread_locks.clear()


def thread_count():
    with lock_for(Thread):
        return len(_thread_locks)


def process_count():
    with lock_for(Process):
        return multiprocessing.cpu_count()


_process_lock: Lock = Lock()

if TYPE_CHECKING:
    from subprocess import Process

else:

    # noinspection PyShadowingNames
    class Process(metaclass=ABCMeta):
        def terminate(self):
            pass

        @property
        def pid(self):
            ...

        @property
        def exitcode(self):
            ...

        def wait(timeout=None):
            ...

        def communicate(input=None, timeout=None):
            ...


try:
    from concurrent.futures import ThreadPoolExecutor as Executor

except ImportError:
    from threading import Thread

    from future_builtins import map

    from concurrent.futures._base import Future

