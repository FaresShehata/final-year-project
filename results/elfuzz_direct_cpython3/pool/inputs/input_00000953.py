"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          decorators, context managers, async/await.
"""

from __future__ import annotations as _annotations

import abc
import asyncio
import enum
import functools
import itertools
import logging
import operator
import os
import pathlib
import pprint
import random
import re
import string
import sys
import timeit
import typing
import warnings

import array

import collections
import collections.abc
import collections.abc as ca

import contextlib
import dataclasses
import datetime
import decimal
import doctest
import fractions
import heapq
import html
import json
import keyword
import linecache
import line_profiler
import locale
import marshal
import mimetypes
import mmap
import multiprocessing
import opcode
import pickle
import platform
import pprint
import queue
import random
import reprlib
import struct
import subprocess
import tarfile
import textwrap
import threading
import tempfile
import time
import types
import traceback
import tokenize
import unicodedata
import urllib.error
import urllib.request
import uuid
import weakref

from io import BytesIO, StringIO
from pathlib import Path

import attr

import attrs
import attrs.validators as av

import attr.validators as av

import backports.zoneinfo

import bisect
import bz2
import calendar
import cdecimal
import collections
import collections.abc
import csv
import ctypes
import datetime
import decimal
import difflib
import dis
import fractions
import ftplib
import functools
import gzip
import http.client
import http.cookiejar
import http.cookies
import http.server
import imaplib
import ipaddress
import itertools
import json
import keyword
import lzma
import lzma  # https://docs.python.org/3/library/lzma.html
import lzma  # https://docs.python.org/3/library/decorator.html
import math
import mimetypes
import mmap
import multiprocessing
import netrc
import nntplib
import numpy
import operator
import optparse
import os
import os.path
import operator
import optparse
import pstats
import pickle
import plistlib
import platform
import poplib
import posixpath
import pprint
import pwd
import py_compile
import pydoc
import quopri
import random
import re
import resource
import select
import shlex
import shutil
import signal
import smtplib
import socket
import sqlite3
import ssl
import stat
import    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    FAILED    = "failed"
    CANCELLED = "cancelled"
    DONE      = "done"


class ShapeType(enum.Enum):
    TRIANGLE     = "triangle"
    SQUARE       = "square"
    RECTANGLE    = "rectangle"
    CIRCLE       = "circle"
    ELLIPSE      = "ellipse"
    PARALLELOGRAM = "parallelogram"
    HEPTAGON     = "heptagon"
    OCTAGON      = "octagon"
    NONAGON      = "nonagon"
    DECAGON      = "decagon"
    HUNDRED_GON  = "100-gon"


# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Person:

    age: int
    name: str
    email: str | None = None

    # This definition of `mails` makes it impossible to use the fast `in`
    # operation on `set`, but allows for efficient lookups with `get`.
    mails: set[str] = dataclasses.field(default_factory=set)

    def full_name(self) -> str:
        return f"{self.name} {self.age}"


# ── Decorators ───────────────────────────────────────────────────────────────-

def memoize(func: Callable[..., T]) -> Callable[..., T]:
    cache: dict[K, V] = {}

    @overload
    def decorator(_: Callable[..., T]) -> Callable[..., T]: ...
    
    @overload
    def decorator(v: K) -> Callable[[Callable[..., T]], Callable[..., T]]: ...
        
    def decorator(v=None) -> Callable[[Callable[..., T]], Callable[..., T]]:
        nonlocal cache
        
        if v is None:
            return lambda func: decorator(func)
            
        return functools.wraps(func)(
            lambda *args, **kwargs: cache.setdefault(v, func(*args, **kwargs))
        )
    
    return decorator


# ── Generics ──────────────────────────────────────────────────────────────────

class FrozenDict(Generic[T], abc.Mapping[T, Any]):
    
    def __init__(self, mapping: Mapping[T, Any]): 
        self._mapping = {}
        self.update(mapping)
    
    def update(self, mapping: Mapping[T, Any]): ... 
        
    def copy(self): ... 

    def __getitem__(self, key) -> Any: raise KeyError        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

