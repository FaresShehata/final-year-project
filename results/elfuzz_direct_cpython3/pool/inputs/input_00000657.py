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
import datetime as dt
import hashlib
import hmac
import io
import itertools
import logging
import mmap
import os
import pathlib
import random
import re
import shutil
import string
import sys
import time
import uuid
from contextlib import (
    AbstractContextManager,
    ContextDecorator,
    closing,
    contextmanager,
)
from email.utils import parseaddr
from enum import Enum, auto
from functools import wraps
from io import TextIOWrapper
from multiprocessing.pool import ThreadPoolExecutor
from operator import itemgetter
from pathlib import Path
from shutil import copy2
from statistics import mean, median, stdev
from threading import Thread
from types import FunctionType, MethodType
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    NewType,
    NoReturn,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)
from urllib.parse import urlparse
from weakref import ref
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED


# 01. Seed 00 — conda install -c conda-forge "typing-extensions==3.10.0"
# -------------------------------------------------------------
def is_bool(x: Any) -> bool:
    return isinstance(x, bool)


def is_int(x: Any) -> bool:
    return isinstance(x, int)


def is_float(x: Any) -> bool:
    return isinstance(x, float)


def is_str(x: Any) -> bool:
    return isinstance(x, str)


def is_bytes(x: Any) -> bool:
    return isinstance(x, bytes)


def is_none(x: Any) -> bool:
    return x is None


def is_list(x: Any) -> bool:
    return isinstance(x, list)


def is_tuple(x: Any) -> bool:
    return isinstance(x, tuple)


def is_set(x: Any) -> bool:
    return isinstance(x, set)


def is_dict(x: Any) -> bool:
    return isinstance(x, dict)


def is_number(x: Any) -> bool:
    return isinstance(x, (int, float))


def is_iterable(x: Any) -> bool:
    # TODO: Make more accurate.
    return hasattr(x, "__iter__")


def is_callable(obj: object) -> bool:
    return callable