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
import json
import math
import os
import pickle
import re
import random
import secrets
import signal
import string
import sys
import threading
import time
import types
import typing
import urllib.request as urlrequest
import zlib
from collections.abc import Iterable, Iterator
from datetime import timedelta
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from queue import Queue
from shlex import quote
from types import TracebackType
from typing import (
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Hashable,
    IO,
    Literal,
    Mapping,
    NoReturn,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeGuard,
    TypedDict,
)
from typing_extensions import NotRequired, Unpack, get_args, get_origin, get_type_hints
from unittest.mock import patch
from uuid import UUID, uuid4

from colorama import Fore, Style
from dateutil.parser import parse as parsedate
from dateutil.tz import tzlocal
from docutils.parsers.rst import Directive
from enum import Enum
from ipaddress import IPv4Address, IPv4Network
from itertools import accumulate, chain, permutations, product
from pathlib import Path
from pprint import pformat
from requests.exceptions import ConnectionError, Timeout
from rich.console import Console
from rich.table import Table
from rich.text import Text
from typing_extensions import Protocol, Self
from xmlrpc.client import ServerProxy

from seed03._types import (
    _AnyPathLike,
    _BinaryIO,
    _CallableT,
    _CallableWithArgsT,
    _CSVRow,
    _FilePathLike,
    _IterableT,
    _JsonSerializableT,
    _MatchT,
    _NoneOr,
    _PathLike,
    _Tuple1T,
    _Tuple2T,
    _UnionT,
)
from seed03.utils import (
    _add_newline_to_stringifys,
    _call_repr_with_arguments,
    _call_str_with_arguments,
    _get_base_url_for_url_which_supports_path,
    _make_tuple_from_iterable,
    _print_table_and_its_output_as_json_if_needed,
    _repr_with_arguments,
    _tupleify,
)

console = Console()

# https://docs.python.org/3/library/stdtypes