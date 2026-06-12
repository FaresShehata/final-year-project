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
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

from docutils.nodes import Text
from icecream import ic
from more_itertools import collapse
from pydantic import BaseModel, BaseSettings, Field, BaseModelConfig
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.table import Table
from rich.text import Text
from rich.traceback import install, TracebackSource, RichTraceback
from rich.columns import Columns
from rich.prompt import Prompt
from rich.style import Style
from rich.theme import Theme
from rich.tree import Tree
from rich.filesize import bytes2human


# Seed 01: Python - Basic Types and Literals
def basic_types() -> None:
    # int
    x = 3600
    print(x)
    assert isinstance(x, int) is True

    # float
    y = 3.1415927
    print(y)
    assert isinstance(y, float) is True

    # complex
    z = 1j * 2 + 3j ** 2 - 4j * 5
    print(z)
    assert isinstance(z, complex) is True

    # bool
    v = True
    w = False
    print(v)
    print(w)
    assert isinstance(v, bool) is True
    assert isinstance(w, bool) is True

    # str
    s = "Hello, World!"
    print(s)
    assert isinstance(s, str) is True

    # bytes
    b = b"Hello, World!"
    print(b)
    assert isinstance(b, bytes) is True

    # bytearray
    ba = bytearray(5)
    for i in range(len(ba)):
        ba[i] = 65 + i
    print(ba)
    assert isinstance(ba, bytearray) is True

    # memoryview
    mv = memoryview(bytes(8))
    print(mv[2])
    assert isinstance(mv, memoryview) is True

    # None, represented by the value None
    n = None
    print(n)
    assert n is None


# Seed 02: Python - Collections and Mapping
def collections_and_mapping() -> None:
    # list
    x = [1]
    print(x)
    assert isinstance(x, list) is True

    # tuple
    t = (x,)
    print(t)
    assert isinstance(t, tuple) is True

   