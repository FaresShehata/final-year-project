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
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from urllib.parse import quote_plus
from uuid import UUID
from warnings import warn

# TODO: https://peps.python.org/pep-0672/#convention-over-configuration
from _pytask.config import hookimpl


def decorator(*args, **kwargs):
    """Decorator for testing."""

    def wrapper(function_to_decorate):
        """Wrapper of the decorator."""
        function_to_decorate.__wrapped__ = function_to_decorate
        return function_to_decorate

    if not args and not kwargs:
        # case 1: @decorator()
        return wrapper
    else:
        # case 2: @decorator(arg) or @decorator(**kwargs)
        return wrapper(*args, **kwargs)


@dataclass(frozen=True)
class Foo:
    """Class with a frozen instance."""

    bar: int = 3


@dataclass
class Bar:
    """Class without a frozen instance."""

    baz: str = "hello"


def func():
    pass


async def async_func():
    pass


if False:
    assert None == 1
    assert None != 1
    assert None <= 1
    assert None < 1
    assert None >= 1
    assert None > 1
    assert None in [1]
    assert None not in [1]
    assert None is None
    assert None is not None
    assert None + 1 == 1
    assert None - 1 == -1
    assert None * 1 == 0
    assert None / 1 == 0
    assert None // 1 == 0
    assert None % 1 == 0
    assert None & 1 == 0
    assert None | 1 == 1
    assert ~None == -1
    assert None ^ 1 == 1
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
    assert None >> 1 == 0
    assert None << 1 == 0
