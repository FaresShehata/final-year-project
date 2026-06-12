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
    assert "ab".rjust(3) == " ab"
    assert "ab".ljust(3) == "ab "
    assert "ab".center(3) == " ab"
    print("X{:<10}Y{:>10}Z{}".format(1, 2, 3))
    print("{:d}".format(1e10))
    print("{:.2f}".format(-1e-8))

    # Seed 02 - None
    assert not [None]
    assert not {None}
    assert not set(None)

    # Seed 03 - Numbers
    assert int('1') == 1
    assert float('-inf') < 0 <= float('+inf')
    assert int(float("-inf")) == -sys.maxsize - 1
    assert int(float("+inf")) == sys.maxsize
    assert str(int()) == '0'
    assert str(bin(10)) == '0b1010'

    # Seed 03 - Complex numbers
    assert abs(complex(0, 0)) == 0
    assert complex(1j).real == 0
    assert complex(1j).imag == 1
    assert round(abs(complex(1, 1)), 9) == 1.414213562
    assert round(abs(complex(1, 1)**2), 9) == 2.0
    assert round(abs(complex(1, 1)**3), 9) == 1.414213562
    assert complex(1, 1) * complex(1, 1) == 2
    assert complex(1, 1) ** 2 == 2
    assert complex(1, 1) ** 3 == 1.414213562e+00
    assert round(abs(complex(1, 1) ** 4), 9) == 1.4142135628
    assert round(abs(complex(1, 1) ** 5), 9) == 2.0
    assert round(abs(complex(1, 1) ** 6), 9) == 1.4142135628

    # Seed 04 - Enumer
    print(re.match("\w+", "This_is_a_test"))

