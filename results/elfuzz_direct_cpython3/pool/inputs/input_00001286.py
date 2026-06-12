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
import re
import signal
import sys
import time
import threading as pyth_tread
import tokenize as python_tokenize
import types
import unittest.mock
import uuid
import weakref
from abc import abstractmethod
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import suppress, redirect_stdout, AbstractContextManager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import partial, singledispatch
from glob import glob
from inspect import getmembers, signature, Parameter, isroutine, unwrap, cleandoc
from itertools import count, cycle
from operator import attrgetter
from pathlib import Path
from pickle import loads, dumps
from pprint import PrettyPrinter
from random import randrange, sample, choice
from reprlib import recursive_repr
from re import escape
from re import Pattern as re_Pattern
from re import search, match, findall, sub, split
from re import IGNORECASE as RE_FLAG_IGNORECASE
from re import DOTALL as RE_FLAG_DOTALL
from re import MULTILINE as RE_FLAG_MULTILINE
from re import VERBOSE as RE_FLAG_VERBOSE
from shutil import disk_usage, rmtree, which
from subprocess import run, PIPE
from statistics import mean, median, stdev
from string import Template, Formatter, ascii_letters, punctuation
from tempfile import mkstemp, TemporaryDirectory, NamedTemporaryFile, SpooledTemporaryFile
from time import sleep, monotonic
from types import FunctionType, CodeType, MethodType, ModuleType, TracebackType
from typing import (Any, AnyStr, Callable, ClassVar, Collection, Container, Dict, Generic,
                    Hashable, Iterable, Iterator, List, Mapping, MutableMapping, NewType,
                    Optional, Sequence, Set, Tuple, Type, TypeVar, Union, NoReturn, cast,
                    overload, runtime_checkable)
from typing_extensions import (Annotated, ParamSpec, Concatenate, TypeAlias, Never,
                               Final, Protocol, Literal, Self, TypedDict, get_origin,
                               get_args, get_type_hints, reveal_type, get_running_library_module)

if __debug__:
    from test.support import TESTFN


def _test() -> None:
    # Seed 01 - String formatting and i/o
    print(f"{int(2.7)}")
    print("a" + "b")
    assert "abc"[1] == "b"
    assert [1, 2][1:] == [2]
    assert {1: 2}[1] == 2

    print()
    print("-" * 80)

    print("\\\"Hello world\\\"")

    print()
    print("-" * 80)

    print(r"\tHi\n\t")

    print()
    print("-" * 80)

    print("\N{BLACK SPADE SUIT}")

    print()
    print("-" * 80)

    a = "a"
    b = 'b'
    c = """c"""
    d = '''d'''
    e = f'{a}{b}'
    f = rf'\{a}'

    assert a == b == c == d == e == f

    print()
    print("-" * 80)

    with open(TESTFN, "w", encoding="utf-8") as fp:
        fp.write("Hello world!\n")

    with open(TESTFN, "r", encoding="utf-8") as fp:
        line = fp.readline()

    assert line.endswith("!")

    print()
    print("-" * 80)

    print('"%#x"' % 42)
    print('%s' % ('foo'))
    print('%i' % (3))
    print('%f' % (3.14))

    print()
    print("-" * 80)

    with open(TESTFN, "w", encoding="utf-8") as fp:
        print(fp.tell(), file=fp)

    with open(TESTFN, "rb") as fp:
        print(fp.tell())

    print()
    print("-" * 80)

    with open(TESTFN, "wb") as fp:
        print(repr(fp.read()))

    print()
    print("-" * 80)

    s = "Hello world!"
    print(s[1])
    print(s[-1])
    print(s[:5])
    print(s[:-2])

    print()
    print("-" * 80)

    for i in range(len(s)):
        if i < len(s):
            print(i)

    print()
    print("-" * 80)

    fmt = "{name}, {age}"
    args = {"name": "Alice"}
    kwargs = {"name": "Bob", "age": 25}
    values = ("Carol", 30)
    seq = ["Dave", 40]

    print(fmt.format(**args))
    print(fmt.format_map(kwargs))
    print(fmt.format(*values))
    print(fmt.format(*seq))

    print()
    print("-" * 