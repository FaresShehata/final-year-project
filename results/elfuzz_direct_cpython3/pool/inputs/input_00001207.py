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
import decimal
import doctest
import email.utils
import enum
import functools
import hashlib
import html
import io
import itertools
import json
import locale
import logging
import math
import mimetypes
import multiprocessing
import os
import pickle
import platform
import random
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import tokenize
import time
import urllib.parse
import uuid
import warnings
import weakref
from collections.abc import Iterable, Mapping, MutableSequence, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from functools import partial
from heapq import heappop, heappush
from itertools import islice
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from queue import Empty, Queue
from reprlib import Repr
from typing import (
    Any,
    Dict,
    Hashable,
    List,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    Tuple,
    Union,
)
from types import ModuleType
from typing_extensions import TYPE_CHECKING, Concatenate, ParamSpec, Self, TypeGuard, Unpack
from unittest.mock import patch


if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec("P")
else:

    class P:
        ...  # pragma: no cover


p1 = namedtuple("p1", ["a", "b"])
p2 = namedtuple("p2", p1._fields + ("c",))


@dataclass(frozen=True)
class C1:
    a: int
    b: float


@dataclass(frozen=True)
class C2:
    a: tuple[int, ...]
    b: float | None = None


# literal_eval
# https://docs.python.org/3/library/ast.html#ast.literal_eval
assert ast.literal_eval("True") == True
assert ast.literal_eval('1+2j') == 1+2j
assert ast.literal_eval('(1+2j)+3*{"a": [None]}') == ((1+2j)+3)*{'a': [None]}
assert ast.literal_eval('[True, False, None]') == [True, False, None]
assert ast.literal_eval('{1: 2}') == {1: 2}
assert ast.literal
def deprecated(reason: str) -> Callable[..., Any]:
    """
    Marks function as deprecated.

    Args:
        reason (str): Reason for deprecation.
    """

    assert reason.startswith("\n"), "reason must start with newline"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        call_args = inspect.signature(func).bind_partial(*sys.argv[1:])
