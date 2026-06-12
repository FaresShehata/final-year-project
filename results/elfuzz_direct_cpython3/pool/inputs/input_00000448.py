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
import pickle
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tokenize
import traceback
import unittest.mock as mock
import weakref
from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from html.parser import HTMLParser
from inspect import Parameter, signature
from itertools import chain
from logging import Logger
from math import isclose, log10
from operator import add, mul
from pathlib import Path
from queue import Queue
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Iterator,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    Protocol,
    Tuple,
    Union,
)
from unittest.mock import patch, call

import pytest
import rich.console
import rich.traceback
from pytest_regressions.file_regression import FileRegressionFixture

try:
    from _pytest.reports import TestReport
except ImportError:
    class TestReport(object):
        pass

try:
    from _pytest.outcomes import Failed
except ImportError:
    class Failed(Exception):
        def __str__(self) -> str:
            return self.args[0]


def test_concurracy():
    """Concurrency."""

    @dataclass(frozen=True)
    class Foo:
        i: int = 0

    # concurrent.futures.ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_1 = executor.submit(Foo.i.__add__, 2)
        future_2 = executor.submit(Foo.i.__add__, 3)

    assert future_1.result() == 2 + 2
    assert future_2.result() == 3 + 3

    # concurrent.futures.ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_1 = executor.submit(Foo.i.__add__, 2)
        future_2 = executor.submit(Foo.i.__add__, 3)

    assert future_1.result() == 2 + 2
    assert future_2.result() == 3 + 3


@pytest.mark.parametrize("cls", [int, float])
def test_literals(cls: type[Any]) -> None:
    """Literal."""
    assert cls(1) == 1
    assert cls(1) != 2
    assert cls(1) in {1}
    assert cls(1) not in {2}
    assert isinstance(cls(1), int)


def test_literal_iterables() -> None:
    """Literal iterables."""
    a = (1,)
    b = tuple([1])

    assert a == b
    assert a != set()
    assert a <= set()

    c = frozenset([1, 2, 3])
    d = frozenset({1, 2, 3})

    assert a == c
    assert a != d
    assert c <= d

    assert a < d

    e = {1: 1}

    assert a == e
    assert a