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
from pprint import pformat, pprint
from queue import Queue, SimpleQueue
from random import shuffle, uniform
from reprlib import RecursiveRepr, repr
from resource import getrusage, RUSAGE_SELF
from statistics import median, mean
from string import Formatter
from types import FrameType, TracebackType
from typing import (
    Any,
    Callable,
    Collection,
    ContextManager,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Pattern,
    Set,
    Tuple,
    Union,
)
from urllib.request import urlretrieve
from weakref import ReferenceType, WeakKeyDictionary, WeakSet

from _pytest.monkeypatch import MonkeyPatch


def test_basic():
    """Basic usage."""
    assert "foo" == foo("bar")
    assert 2 + 2 == 4
    assert float(3) / 2 == 1.5
    assert int(float(3)) == 3
    # TODO: This should be a TypeError or similar?
    # assert not True and False
    assert -(1 - 1j) == (-1+1j)


def test_grammar():
    """Grammar tests."""
    assert 1 < 2 <= 3 >= 3 > 2 != 1

    assert bool(0) == False
    assert str(bool(0)) == 'False'
    assert isinstance(bool(0), bool)

    assert all([True])
    assert any([True])
    assert not all([])
    assert not any([])

    assert sorted(((), (), ('a',))) == [('a'), ()]
    assert sorted(('()'), key=len) == [()]

    assert range(10)[:5] == range(0, 5)
    assert list(range(10)[:5]) == [0, 1, 2, 3, 4]
    assert tuple(range(10)[:5]) == (0, 1, 2, 3, 4)
    assert set(range(10)[:5]) == {0, 1, 2, 3, 4}

    assert abs(-1) == 1
    assert round(1.99999) == 2
    assert round(1.99999, 2) == 2.00
    assert pow(2, 3) == 8
    assert pow(2, 3, 7) == 6
    assert eval('1 + 2') == 3
    assert eval('3 ** 3') == 27
    assert eval('"Hello {}!".format("World")') == 'Hello World!'
    assert eval(repr(abs)) == abs

    assert complex(1) == 1j
    assert complex(0, 1) == 1j
    assert complex(1, 0) == 1
    assert complex(-1, -1).real == -1
    assert complex(-1, -1).imag == -1
    assert complex(1, 1).real == complex(1).real
    assert complex(1, 1).imag == complex(1).imag
    assert complex(0.0, 0.0) == 0.0
    assert complex(0.0, 0.0j) == 0.0j
    assert complex(0.0, 0.0j+0.0) == 0.0j

    assert len(str(None)) == 4
    assert sum([1, 2]) == 3
    assert min([1, 2]) == 1
    assert max([1, 2]) == 2
    assert reversed([1, 2])[::-1] == [2, 1]

    assert divmod(10, 3) == (3, 1)

    assert chr(ord('\x41')) == '\x41'


def test_special():
    """Special functions."""
    assert all([i for i in range(5)]) == 10
    assert all([i for i in range(5)][::2]) == 5

    assert any([i for i in range(5)]) == True
