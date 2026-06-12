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
import time
import traceback
import types
import uuid
import warnings
from collections.abc import Callable, Generator, Iterable, Iterator, Sized
from concurrent import futures as cfutures
from concurrent.futures._base import Future, Executor
from collections import defaultdict
from enum import Enum, IntEnum, auto
from functools import lru_cache, partialmethod, wraps
from itertools import count
from logging import LoggerAdapter, getLogger
from math import log1p, floor, ceil, sqrt
from operator import attrgetter, methodcaller
from pathlib import Path
from pprint import pformat
from queue import Queue, Empty
from re import Pattern
from string import Formatter
from textwrap import fill
from typing import TYPE_CHECKING, Any, NamedTuple, Optional, Sequence, Tuple, Union, cast, overload
from urllib.parse import quote_plus

# https://docs.python.org/3/library/typing.html#module-typing
from typing_extensions import Literal, ClassVar, TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Annotated, get_type_hints, reveal_type


def _print_func(func: Callable[..., Any], name: str = None) -> None:
    """Print the docstring and source code of a function."""
    if func.__doc__ is not None:
        print(fill(func.__doc__, width=80))
    if name:
        print(f"Source code for {name}:")
    else:
        print("Source code:")
    src_lines = inspect.getsource(func).split("\n")
    for src_line in src_lines[2:]:
        print(src_line)


def _print_summary(func: Callable[..., Any]) -> None:
    """Print a summary of a function."""
    if isinstance(func, property):
        return _print_property(func)
    # Check if func has a docstring or an attribute named "description"
    docstr = getattr(func, "__doc__", "")
    description = getattr(func, "description", "")
    if docstr and len(docstr.strip()) > 0:
        print(pformat(docstr))
    elif description and len(description.strip()) > 0:
        print(description)
    else:
        print(repr(func))
    print()
    _print_func(func)
    print()


def _print_property(prop: property) -> None:
    """Print a summary of a property."""
    desc: str = getattr(prop, "description", "")
    value: object