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
    print(r'"\'\n\r\t\v\f\b"'[3:-1])
    print(r'The quick brown fox jumps over the lazy dog.')
    print(r'He said, "\x01\x02\x03"')
    print(r'\t\n\f\r\v')
    print(r'\u{1F4A9}')

    print()

    print(chr(ord('"')))
    print(ord('\t'))
    print(oct(12))
    print(hex(12))

    print()

    p = Path(sys.executable)
    print(p.name)
    print(p.stem)
    print(p.suffix)
    s = Path.home().stem
    print(s[-len(str(datetime.now()))-1])

    print()

    print(Path.cwd())
    print(os.getcwd())

    print()

    print(Path.home())
    print(os.path.expanduser('~'))

    print()

    p1 = Path(__file__)
    print(p1.resolve())
    print(p1.absolute())

    print()
    print(Path.pardir)
    print((Path('/tmp') / 'foo/bar').parent)
    print((Path('/tmp') / 'foo/bar').parents)
    print((Path('.cache') / '..').parent.parent)
    print((Path('/') / '/foo/../../bar/baz').absolute())
    print((Path('/foo/') / '../bar').resolve())

    print()

    p = Path('.')
    for file in p.glob('*'):
        if not file.is_dir():
            print(file.relative_to('/'))

    print()

    with open(TESTFN, 'wb+') as f:
        f.write(b'ABCDEF')
    with open(TESTFN, 'rb') as f:
        for line in iter(lambda: f.readline(), b''):
            print(line.strip())
    print(open(TESTFN).name)
    os.remove(TESTFN)
    print(escape('\\\t\n\f\r\v \\ \" \\' % '\n\t'))

    print()

    print("\x1B[1;32mHello World!\x1B[0m".encode())
    print(repr("\x1B[1;32mHello World!\x1B[0m".encode()))

    print()

    print("{:c}".format('A'))
    print("{:#x}\n".format('A'))
    print("{:+d}\n".format(-10))
    print("{:,}".format(1000000000))
    print("{:.2f}".format(10/3))
    print("{:<10.2f}".format(10/3))
    print("{:>10.2f}".format(10/3))
    print("{:^10.2f}".format(10/3))
    print("{:*^10.2f}".format(10/3))
    print("{:*>10}.format('hello')")
    print("{:-<10}.format('hello')")
    print("+{:>10,.2f}+ ".format(1e7))
    print("|{:>10,.2f}| ".format(1e7))
    print(" {:>10,.2f} ".format(1e7))
    print("{} {:>10,.2f} ".format('hello', 1e7))
    print("{!s} {!r} {!a}".format('str',