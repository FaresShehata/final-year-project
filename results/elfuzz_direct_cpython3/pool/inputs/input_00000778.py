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

    assert zip([(1,), (2,)], [(3,), (4,)]) == ((1, 3), (2, 4))
    assert set(zip([(1,), (2,)], [(3,), (4,)])) == {tuple(x) for x in zip([(1,), (2,)], [(3,), (4,)])}
    assert tuple(zip([(1,), (2,)], [(3,), (4,)])) == ((1, 3), (2, 4))

    assert map(lambda x: x, []).next