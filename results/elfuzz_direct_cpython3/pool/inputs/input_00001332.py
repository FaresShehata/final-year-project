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
from string import Template, Formatter, ascii_letters, punctuations
from string import ascii_lowercase, digits, hexdigits
from struct import pack
from sys import intern
from sys import argv as sys_argv
from sys import maxsize as sys_maxsize
from sys import path as sys_path
from tempfile import TemporaryDirectory as TempDir
from tempfile import NamedTemporaryFile as NTempFile
from textwrap import dedent
from textwrap import indent
from textwrap import fill
from textwrap import wrap
from textwrap import TextWrapper
from textwrap import wrap as textwrap_wrap
from textwrap import shorten
from textwrap import TextWrapper as TextWrapper_TextWrapper
from textwrap import dedent as textwrap_dedent
from textwrap import indent as textwrap_indent
from textwrap import fill as textwrap_fill
from thread import allocate_lock, LockType
from traceback import format_exception as trace_format_exc
from traceback import extract_stack as trace_extract_stack
from traceback import format_tb as trace_format_tb
from typing import TYPE_CHECKING
from typing import Counter
from typing import DefaultDict
from typing import Deque
from typing import Dict
from typing import List
from typing import ItemsView
from typing import Iterator
from typing import KeysView
from typing import Mapping
from typing import MutableMapping
from typing import NewType
from typing import NoReturn
from typing import Optional
from typing import OrderedDict
from typing import OrderedDict
from typing import Params
from typing import Pattern
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import ValueErrors
from typing import ValuesView
from typing import cast
from typing import final
from typing import overload
from typing import runtime_checkable
from typing import Sequence
from typing import Callable
from typing import _extract_args
from typing import _eval_type
from typing import _type_vars_from_call
from typing import _resolve_annotations
from typing import _generic_rebind
from typing import _get_type_hints
from typing import _verify_protocol
from typing import _check_generic
from typing import _GenericAlias
from typing import _SpecialForm
from typing import _Union
from typing import _ForwardRef
from typing import _alias
from typing import _eval_type
from typing import _eval_final_annotation
from typing import _eval_constant_expression
from typing import _eval_type_arguments
from typing import _eval_unbound_function
from typing import _eval_bound_function
from typing import _eval_methods
from typing import _eval_callable
from typing import _eval_annotated
from typing import _eval_union_alias
from typing import _eval_literal
from typing import _eval_type_var
from typing import _eval_type_param
from typing import _eval_inferred_typevar
from typing import _eval_inferred_typeparams
from typing import _eval_inferred_typevars
from typing import _eval_inferred_typevar_aliases
from typing import _eval_inferred_typeparam_aliases
from typing import _eval_inferred_typevar_bindings
from typing import _eval_inferred_typeparam_bindings
from typing import _eval_inferred_typevar_binding
from typing import _eval_inferred_typeparam_binding
from typing import _eval_inferred_typevar_binding_of_typevar
from typing import _eval_inferred_typeparam_binding_of_typevar
from typing import _eval_inferred_typevar_binding_of_typeparam
from typing import _eval_inferred
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
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20

def positive_short_str(x) -> bool:
    return positive(x) and short_str(x)

class X(_Constrained):
    pass
X = Annotated[X, positive, short_str]

class Y(X): # type: ignore
    pass
Y = Annotated[Y, positive, short_str]

@Annotated["X", {"max": 10}]
def foo(x):
    pass
foo(-1)

# ── Annotated with a custom validator ────────────────────────────────────────

from typing_extensions import Annotated

A: Annotated[int, lambda n: True]
B: Annotated[int, lambda n: n == 10]

assert A == B
assert A != 10

# ── Annotated with multiple validators ───────────────────────────────────────

C: Annotated[int, lambda n: n >= 0, lambda n: n % 3 == 0]
D: Annotated[int, lambda n: n >= -100, lambda n: n % 7 == 0]

assert C == D == 12
assert C < 9
assert D <= -86
assert C + D == 24
assert C * D == 144

# ── TypedDict with no mandatory keys ─────────────────────────────────────────

MyDict: TypeAlias = TypedDict("MyDict", {str: str}, total=False)

my_dict = MyDict()
print(my_dict)

# ── TypedDict with non-optional keys ─────────────────────────────────────────

MyOtherDict: TypeAlias = TypedDict("MyOtherDict", {
    "id":      int,
    "email":   Annotated[str, "@"],
})

my_other_dict = MyOtherDict(id=1, email="user@example.com")
print(my_other_dict)

