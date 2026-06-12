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

    print('She said, "hello world"')

    print()

    print("""She said,
    "hello world."
	""")

    print()

    print(r'"\t"')

    print()

    print('''"\t"''')

    print()
    # Seed 02 - Regular expressions
    pattern = re.compile(r"(?P<name>\w+)@(\w+)", flags=RE_FLAG_IGNORECASE | RE_FLAG_DOTALL)
    matches = pattern.match("joe@example.com")
    if matches:
        name, host = matches.groups()
        print(name, host)

    pattern = re.compile(r"\d+", flags=re.MULTILINE)
    for line in ("one\n", "two\n"):
        print(pattern.findall(line))

    assert isinstance(re.search("\d", "\t"), type(None))
    assert isinstance(re.fullmatch(r"\d", "1"), type(None))
    assert isinstance(re.match("\d", "\n"), type(None))
    assert isinstance(re.split(",", "a,b,c,d"), list)
    assert isinstance(re.sub(", ", ";", "a,b,c,d"), str)
    assert isinstance(re.escape('"'), str)
    assert isinstance(re.escape('"', escape="\\"), str)
    assert isinstance(re.escape('"', escape=r"\\"), str)
    assert isinstance(re.escape('"', escape="\\\\\\"), str)
    assert isinstance(re.escape('\\u{u}'), str)
    assert isinstance(re.escape('\ud83d\ude03'), str)
    assert isinstance(re.escape('\ud83d\ude03', escape='x'), str)
    assert isinstance(re.escape('\ud83d\ude03', escape='\x'), str)
    assert isinstance(re.escape('\ud83d\ude03', escape='\\x'), str)
    assert isinstance(re.escape('\\u{u}', escape='x'), str)
    assert isinstance(re.escape('\\u{u}', escape='\x'), str)
    assert isinstance(re.escape('\\u{u}', escape='\\x'), str)
    assert isinstance(match(r"\d", ""), bool)
    assert isinstance(search(r"\d", "", flags=RE_FLAG_IGNORECASE), type(None))
    assert isinstance(findall(r"\d", ""), list)
    assert isinstance(sub(r"\d", "", "", flags=RE_FLAG_IGNORECASE), str)
    assert isinstance(split(r"\d", "", maxsplit=1), list)
    assert isinstance(punctuation, str)
    assert isinstance(escape('"' ' "''""'), str)
    assert isinstance(punctuation, str)
    assert isinstance(ascii_letters, str)
    assert isinstance(cycle([1, 2]), Iterator[int])
    assert isinstance(count(),