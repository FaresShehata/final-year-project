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
import queue
import secrets
import string
import re
import sys
import tempfile
import textwrap
import tokenize
import types
import unittest.mock
import warnings
import webbrowser
from collections import deque
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from functools import partial
from inspect import Signature
from inspect import signature
from operator import itemgetter
from timeit import Timer
from types import TracebackType
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Generator
from typing import Generic
from typing import List
from typing import Optional
from typing import Pattern
from typing import Set
from typing import Tuple
from typing import Type
from typing import Union
from typing import ValuesView
from typing_extensions import Annotated
from typing_extensions import SupportsIndex
from typing_extensions import TypedDict
from typing_extensions import Unpack
from typing_extensions import get_args
from typing_extensions import get_origin
from typing_extensions import get_type_hints
from typing_extensions import reveal_type
from typing_extensions import reveal_type_stub
from typing_extensions import self_param
from typing_extensions import self_params
from typing_extensions import SelfParam
from typing_extensions import SupportsIndexStub
from typing_extensions import VarArg
from typing_extensions import Void
from typing_extensions import _Annotator
from typing_extensions import _AnyCallable
from typing_extensions import _AnnotatedAlias
from typing_extensions import _ClassAnnotationMixin
from typing_extensions import _FinalSet
from typing_extensions import _ForwardRef
from typing_extensions import _GenericAlias
from typing_extensions import _LiteralSpecialForm
from typing_extensions import _ProtocolMeta
from typing_extensions import _UnionSpecialForm
from typing_extensions import get_origin_stubs
from typing_extensions import get_overloads
from typing_extensions import get_type_hints_stubs
from typing_extensions import get_valid_type_hints
from typing_extensions import get_type_hints_stub
from typing_extensions import get_type_vars
from typing_extensions import get_typevars_from_annotated
from typing_extensions import get_typevars_from_union
from typing_extensions import has_finals
from typing_extensions import has_finesse
from typing_extensions import is_protocol
from typing_extensions import is_typeddict
from typing_extensions import no_type_check
from typing_extensions import overload
from typing_extensions import Protocol
from typing_extensions import SupportsInt
from typing_extensions import TypeGuard
from typing_extensions import verify_protocol
from typing_extensions import VOID
from typing_extensions import var_arg

def func(**kwargs: Kwargs) -> None:
    ...


func(name=str, age=int)


# ── GetTypeHints ────────────────────────────────────────────────────────────

def get_type_hints_with_annotations(func: Callable[P, T]) -> dict[str, type[Any]]:
    return get_type_hints(func, globalns=func.__globals__)


get_type_hints_with_annotations(get_type_hints_with_annotations)
# {'func': <class 'function'>}

# ─── RevealType Stub ────────────────────────────────────────────────────────

reveal_type(123)
reveal_type("hello world")
reveal_type([1, 2, 3])
reveal_type(UserRecord())
reveal_type(UserKey(name=str))

reveal_type(str.split())
reveal_type((lambda x: True)(x))
reveal_type(lambda x: x + 1(x))


# ── ContextLib ──────────────────────────────────────────────────────────────

with open(pathlib.Path(__file__)) as f:
    print(f.read())

print()

with contextlib.redirect_stderr(None) as stderr:
    print(stderr.getvalue())
    print('Hello, World!')


# ── Numbers ABC ─────────────────────────────────────────────────────────────

assert isinstance(1.0 * 1.0, numbers.Real)
assert isinstance(-0.0, numbers.Number)
assert not isinstance(object(), numbers.Real)
assert not isinstance([], numbers.Number)

# ── Pathlib ─────────────────────────────────────────────────────────────────

pathlib.Path.cwd()
pathlib.PurePath("/usr/bin") / pathlib.PurePath("ls")


# ── Tempfile ───────────────────────────────────────────────────────────────

tempfile.gettempdir()
tempfile.TemporaryDirectory(prefix="my-unique-prefix", dir=tempfile.gettempdir())


# ── CSV ────────────────────────────────────────────────────────────────────

csv.writer(io.StringIO()).writerow(["foo", "bar"])
csv.reader(io.StringIO("spam,bagel\neggs,milk")).__next__()
list(csv.DictReader(io.StringIO("foobar\nbazquux")))



# ── Base64 ─────────────────────────────────────────────────────────────────

base64.b85decode(b"qQ==")
base64.b93decode(b"qQ==")
base64.b16decode("7E")
base64.b16encode(bytes(1))
base64.b16encode(bytes([1]))
base64.b16encode(bytearray(b"\x7e"))
base64.b16encode(memoryview(b"\x7e"))


# ── Hashlib ─────────────────────────────────────────────────────────────────

hashlib.md5(b"abc").hexdigest()


