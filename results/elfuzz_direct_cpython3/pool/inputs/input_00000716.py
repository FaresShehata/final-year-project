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

    print(b"abc".decode())
    print(bytes([97, 98, 99]).decode())

    print()

    print(ord("'"))
    print(chr(39))

    print()

    print(round(0.1))
    print(round(-0.1))

    print()

    print(float(5), float("5"))
    print(int(True), int(False))

    print()

    a = b = c = 1
    d, e, f = 1, 2, 3
    g, h, i = range(3)
    j, k, l = [1, 2, 3]

    print(a, b, c, d, e, f, g, h, i, j, k, l)

    print()

    print(bin(8))
    print(hex(8))
    print(oct(8))

    print()

    x = 5
    y = 10
    if ((x < 10) and (y > 1)):
        pass

    print()

    for i in range(5):
        pass

    while True:
        break

    for i in range(5):
        continue
    else:
        pass

    print()

    def foo(x: int, y: str, z: bool = False) -> None:
        return

    foo(10, 'x', True)

    print()

    print(dir(__builtins__))
    print(dir(str.__dict__))
    print((dir(unittest.mock)))

    print()

    print(type(None))
    print(isinstance(None, type(None)))
    print(isinstance(None, object))

    print()

    print(not None)
    print(bool(None))
    print(None or True)
    print(None and False)

    print()

    print(all([]))
    print(any([]))

    print()

    print(list(range(5)))
    print(tuple(range(5)))
    print(set(range(5)))
    print(dict(zip(range(5), range(5))))
    print(reversed(range(5)))
    print(sorted(range(5)))
    print(list(map(lambda x: x ** 2, range(5))))

    print()

    print(sum(range(5)))
    print(max(range(5)))
    print(min(range(5)))
    print(abs(-5))
    print(pow(2, 4))

